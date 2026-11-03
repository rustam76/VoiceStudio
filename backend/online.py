"""Server-only composition of VoiceStudio's existing TTS, auth, storage and MCP.

Run with PYTHONPATH=backend python -m uvicorn online:app --port 3900 --workers 1.
No desktop bridge, setup installer, ASR warm-up, or automatic model download.
"""
from __future__ import annotations

import asyncio
import contextlib
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from core.auth import CredentialTransport, PrincipalKind, principal_for, remote_api_key
from core.browser_guard import BrowserGuardMiddleware
from core.csrf import SAFE_HTTP_METHODS, cookie_csrf_allowed
from core.online_policy import generation_policy
from core.version import APP_VERSION

logger = logging.getLogger("voicestudio.online")


def public_path(path: str) -> bool:
    return path in {"/", "/index.html", "/health", "/favicon.ico",
                    "/early-error-capture.js", "/api/auth/session"} or path.startswith("/assets/")


class OnlineAccess:
    """Require the existing key/session on every private path, even behind localhost proxies."""

    def __init__(self, app):
        self.app = app
        self.generating = False

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        request = Request(scope)
        path = scope.get("path", "")
        if not public_path(path):
            principal = principal_for(request)
            if principal.kind not in {PrincipalKind.API_KEY, PrincipalKind.ADMIN_SESSION}:
                return await JSONResponse({"detail": "API key required"}, 401)(scope, receive, send)
            if (request.method not in SAFE_HTTP_METHODS
                    and principal.transport == CredentialTransport.COOKIE
                    and not cookie_csrf_allowed(request)):
                return await JSONResponse({"detail": "browser origin rejected"}, 403)(scope, receive, send)

        # Bound the body before multipart/JSON parsing, including chunked uploads.
        # MCP requests contain text, never reference-audio uploads in this profile.
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body.extend(message.get("body", b""))
            if len(body) > 65536:
                return await JSONResponse({"detail": "Request body exceeds 64 KiB"}, 413)(scope, receive, send)
            if not message.get("more_body", False):
                break
        delivered = False

        async def bounded_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        # No queue of waiting text/audio buffers. Existing guarded executor also
        # retains occupancy when a client cancels an underlying inference.
        generating = path == "/generate" and request.method == "POST"
        if generating and self.generating:
            return await JSONResponse({"detail": "Inference busy; retry later"}, 429,
                                      headers={"Retry-After": "5"})(scope, bounded_receive, send)
        if generating:
            self.generating = True

        async def marked_send(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).extend([
                    (b"x-omnivoice-backend", APP_VERSION.encode()),
                    (b"cache-control", b"no-store"),
                    (b"x-content-type-options", b"nosniff"),
                ])
            await send(message)

        try:
            await self.app(scope, bounded_receive, marked_send)
        finally:
            if generating:
                self.generating = False


@asynccontextmanager
async def lifespan(app):
    from core.db import init_db
    from services import model_manager as mm, tts_backend
    init_db()
    mm.reset_shutdown_flag()
    async def release_idle():
        while True:
            await asyncio.sleep(30)
            await asyncio.to_thread(tts_backend.release_idle_engines)
    idle = asyncio.create_task(release_idle())
    try:
        async with app.state.mcp_session_manager.run():
            yield
    finally:
        idle.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await idle
        mm.begin_shutdown()
        await asyncio.to_thread(tts_backend.release_idle_engines, idle_seconds=0)
        await asyncio.to_thread(mm.shutdown_watermark_pool)


def create_app() -> FastAPI:
    if not remote_api_key():
        raise RuntimeError("OMNIVOICE_API_KEY is required for VoiceStudio Online")
    os.environ["OMNIVOICE_ONLINE"] = "1"
    os.environ["OMNIVOICE_SERVER_MODE"] = "1"
    os.environ["OMNIVOICE_TTS_BACKEND"] = "supertonic3"
    for key, value in {"OMNIVOICE_GPU_WORKERS": "1", "OMNIVOICE_CPU_POOL": "1",
                       "OMNIVOICE_LLM_BACKEND": "off", "OMNIVOICE_IDLE_TIMEOUT": "300",
                       "OMNIVOICE_ENGINE_IDLE_UNLOAD_SECONDS": "300",
                       "OMNIVOICE_TEXT_NORMALIZATION": "0"}.items():
        os.environ.setdefault(key, value)

    from api.routers import auth, generation, model_licenses, profiles
    from core.config import OUTPUTS_DIR
    from services.model_acceptance import ModelLicenceNotAccepted
    from engines.supertonic3.constants import VOICE_PRESETS, MODEL_REPO_ID
    from mcp_server import mount_mcp

    app = FastAPI(title="VoiceStudio Online", version=APP_VERSION, lifespan=lifespan,
                  docs_url="/docs", redoc_url=None)
    app.state.online = True
    app.include_router(auth.router)
    # Preserve upstream endpoint implementations, while omitting clone/admin/
    # arbitrary filesystem APIs and unused license-install machinery.
    allowed = {"/generate", "/generate/budget", "/history", "/history/{history_id}/starred",
               "/history/{history_id}", "/audio/{audio_id}.ogg", "/audio/{audio_id}.opus",
               "/profiles", "/personalities", "/models/licenses/acceptance/{repo_id:path}",
               "/models/licenses/details/{repo_id:path}", "/models/licenses/accept",
               "/models/licenses/revoke"}
    for router in (generation.router, profiles.router, model_licenses.router):
        for route in router.routes:
            if route.path in allowed and not (route.path == "/profiles" and "GET" not in route.methods):
                app.router.routes.append(route)

    @app.exception_handler(ModelLicenceNotAccepted)
    async def licence_required(request, exc):
        return JSONResponse({"detail": exc.detail()}, 403)

    @app.exception_handler(Exception)
    async def failed(request, exc):
        # Do not copy provider exception bodies, paths, input text or secrets.
        logger.error("Online request failed: %s", type(exc).__name__)
        return JSONResponse({"detail": "Generation failed; check server configuration and model installation."}, 500)

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": APP_VERSION, "device": "cpu"}

    @app.get("/engines")
    async def engines():
        return {"tts": {"active": "supertonic3", "backends": [{"id": "supertonic3",
                "model": MODEL_REPO_ID, "preset_voices": VOICE_PRESETS}]}, "asr": {}, "llm": {}}

    @app.get("/languages")
    async def languages():
        return [{"code": "id", "name": "Indonesian"}]

    if not mount_mcp(app):
        raise RuntimeError("MCP is required for VoiceStudio Online")
    app.mount("/audio", StaticFiles(directory=OUTPUTS_DIR, follow_symlink=False), name="audio")
    dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
    app.add_middleware(OnlineAccess)
    app.add_middleware(BrowserGuardMiddleware, is_public_path=public_path)
    return app


app = create_app()
