"""Opt-in real-model acceptance test; uses a separately provisioned QA instance.

Set OMNIVOICE_API_KEY and VOICESTUDIO_TEST_URL. Set ONLINE_QA_ACCEPT_LICENSE=1
only after reviewing the licence, on a disposable QA instance. No downloads.
Outputs samples and measured timings to ONLINE_TEST_RESULTS (default /tmp).
"""
import asyncio
import io
import json
import os
from pathlib import Path
import time
import wave

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

TEXTS = [
    "Halo semuanya! Selamat datang di channel kami. Hari ini kita akan membahas perkembangan teknologi kecerdasan buatan di Indonesia. Bagaimana teknologi ini mengubah cara kita bekerja, belajar, dan membuat konten digital?",
    "Pada tahun 2026, teknologi AI berkembang semakin cepat. Misalnya, kita dapat menggunakan Python, Docker, API, dan Text-to-Speech untuk menghasilkan narasi video secara otomatis.",
]


async def main():
    base = os.environ.get("VOICESTUDIO_TEST_URL", "http://127.0.0.1:3900").rstrip("/")
    headers = {"Authorization": "Bearer " + os.environ["OMNIVOICE_API_KEY"]}
    output = Path(os.environ.get("ONLINE_TEST_RESULTS", "/private/tmp/voicestudio-online-results"))
    output.mkdir(parents=True, exist_ok=True)
    results = []
    async with httpx.AsyncClient(base_url=base, headers=headers, timeout=600) as client:
        assert (await client.get("/health")).status_code == 200
        for path in ("/history", "/mcp", "/audio/12345678.wav"):
            assert (await client.get(path, headers={"Authorization": "Bearer wrong"})).status_code == 401
        for text in ("", "a" * 6001):
            assert (await client.post("/generate", data={"text": text})).status_code == 422
        state = (await client.get("/models/licenses/acceptance/Supertone/supertonic-3")).json()
        if not state["accepted"] and os.environ.get("ONLINE_QA_ACCEPT_LICENSE") == "1":
            response = await client.post("/models/licenses/accept", json={
                "repo_id": "Supertone/supertonic-3", "fingerprint": state["fingerprint"], "accepted": True})
            response.raise_for_status()
        for index, text in enumerate(TEXTS, 1):
            started = time.perf_counter()
            response = await client.post("/generate", data={"text": text, "preset_voice": "M1",
                "num_step": "8", "effect_preset": "raw", "postprocess_output": "false"})
            if response.status_code != 200:
                raise RuntimeError(f"Generation {index}: HTTP {response.status_code}: {response.text[:800]}")
            elapsed = time.perf_counter() - started
            with wave.open(io.BytesIO(response.content)) as audio:
                duration = audio.getnframes() / audio.getframerate()
                assert audio.getframerate() == 44100 and duration > 0
                assert audio.getnchannels() == 1
            audio_id = response.headers["x-audio-id"]
            saved = await client.get(f"/audio/{audio_id}.wav")
            assert saved.content == response.content
            path = output / f"indonesian-{index}.wav"
            path.write_bytes(response.content)
            results.append({"sample": index, "text": text, "audio_id": audio_id,
                "elapsed_s": round(elapsed, 3), "duration_s": round(duration, 3),
                "bytes": len(response.content), "rtf": round(elapsed / duration, 3)})
            print(json.dumps(results[-1], ensure_ascii=False), flush=True)
        history = (await client.get("/history")).json()
        assert {r["audio_id"] for r in results} <= {r["id"] for r in history}

    async with streamable_http_client(base + "/mcp", http_client=httpx.AsyncClient(headers=headers, timeout=600)) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert "generate_speech" in {tool.name for tool in tools.tools}
            result = await session.call_tool("generate_speech", {"text": "Ini adalah pengujian MCP bahasa Indonesia.", "steps": 8})
            assert not result.isError, result
            (output / "mcp-result.json").write_text(result.model_dump_json(indent=2))
    (output / "measurements.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print("API, audio download, history and real Streamable HTTP MCP passed.")


if __name__ == "__main__":
    asyncio.run(main())
