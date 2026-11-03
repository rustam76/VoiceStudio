"""Online composition uses the real upstream routes; no model download in tests."""
import importlib
import asyncio

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def online(monkeypatch):
    monkeypatch.setenv("OMNIVOICE_API_KEY", "online-test-key-with-enough-entropy")
    monkeypatch.setenv("OMNIVOICE_ONLINE", "1")
    module = importlib.import_module("online")
    with TestClient(module.create_app(), client=("127.0.0.1", 1234)) as client:
        yield client


KEY = {"Authorization": "Bearer online-test-key-with-enough-entropy"}


def test_online_requires_key_even_on_loopback(online):
    for path in ("/history", "/engines", "/audio/12345678.wav", "/mcp"):
        assert online.get(path, follow_redirects=False).status_code == 401
    assert online.get("/health").status_code == 200
    assert online.get("/history", headers=KEY).status_code == 200


def test_online_refuses_blank_key(monkeypatch):
    monkeypatch.setenv("OMNIVOICE_API_KEY", " ")
    from online import create_app
    with pytest.raises(RuntimeError, match="OMNIVOICE_API_KEY"):
        create_app()


@pytest.mark.parametrize("data", [
    {"text": " "}, {"text": "a" * 6001},
    {"text": "Halo", "engine": "omnivoice"},
    {"text": "Halo", "speed": "nan"},
    {"text": "Halo", "profile_id": "clone"},
    {"text": " [pause 10s]" * 500},
])
def test_online_rejects_input_before_model_load(online, data):
    assert online.post("/generate", data=data, headers=KEY).status_code == 422


def test_online_body_limit(online):
    assert online.post("/generate", content=b"x" * 65537, headers=KEY).status_code == 413


def test_online_session_and_csrf(online):
    response = online.post("/api/auth/session", json={"transport": "cookie"}, headers=KEY)
    assert response.status_code == 204
    assert "HttpOnly" in response.headers["set-cookie"]
    assert online.get("/history").status_code == 200
    assert online.post("/generate", data={"text": "Halo"}).status_code == 403


def test_online_optional_features_are_absent(online):
    for path in ("/profiles", "/system/info", "/dub", "/api/settings"):
        assert online.post(path, headers=KEY).status_code in (404, 405)


def test_online_audio_path_confined(online):
    assert online.get("/audio/%2e%2e%2fomnivoice.db", headers=KEY).status_code == 404


def test_online_default_language_and_engine():
    from online import generation_policy
    assert generation_policy(text="Pada tahun 2026, teknologi AI.", language=None,
                             engine=None, speed=1.0, profile_id=None, ref_audio=None,
                             instruct=None, design_recipe=None, max_chunk_chars=800) == "id"


@pytest.mark.model_licence_gate
def test_online_model_licence_stays_required(online):
    response = online.post("/generate", data={"text": "Halo Indonesia!"}, headers=KEY)
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "model_licence_required"


def test_online_mcp_tools_and_authenticated_internal_calls(online):
    from mcp_server import create_mcp_server
    server = create_mcp_server(online.app)

    async def check():
        tools = await server.list_tools()
        names = {tool.name for tool in tools}
        assert {"generate_speech", "list_voices", "list_languages", "check_health"} <= names
        assert not names & {"clone_voice", "transcribe", "design_voice", "describe_voice"}
        languages = await server.call_tool("list_languages", {})
        assert '646' not in str(languages)
        result = await server.call_tool("check_health", {})
        assert '"status": "ok"' in str(result)
    asyncio.run(check())


def test_online_missing_model_is_reported(online, monkeypatch):
    from services import tts_backend
    from engines.supertonic3 import Supertonic3Backend
    monkeypatch.setattr(tts_backend, "ensure_engine_licence", lambda cls: None)
    monkeypatch.setattr(Supertonic3Backend, "is_available", classmethod(lambda cls: (False, "model missing")))
    response = online.post("/generate", data={"text": "Halo Indonesia!"}, headers=KEY)
    assert response.status_code == 400
    assert "model missing" in response.json()["detail"]
