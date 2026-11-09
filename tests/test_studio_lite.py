"""Focused deployment must keep real reference conditioning and avoid heavy services."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))


class StudioLiteTests(unittest.TestCase):
    def test_diarisation_status_is_disabled_with_a_pruned_catalogue(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from api.routers.engines import router
        app = FastAPI()
        app.include_router(router)
        with patch.dict(os.environ, {"OMNIVOICE_STUDIO_LITE": "1"}), \
             patch("api.routers.setup.models.KNOWN_MODELS", []):
            response = TestClient(app).get("/engines/diarisation")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["active"], "off")
        self.assertFalse(response.json()["installed"])
        self.assertEqual(response.json()["options"], [])

    def test_diarisation_inventory_tolerates_an_absent_pyannote_entry(self):
        from services.diarization_runtime import installed_backends
        with patch("api.routers.setup.models.KNOWN_MODELS", []), \
             patch("api.routers.setup.models.is_cached") as cached, \
             patch("services.diarization_runtime.sortformer_status", return_value={"installed": False}):
            self.assertEqual(installed_backends(), set())
        cached.assert_not_called()

    def test_no_implicit_model_download(self):
        from engines.openvoice_v2.converter import Converter
        calls = []
        def missing(*args, **kwargs):
            calls.append(kwargs)
            raise FileNotFoundError("empty offline cache")
        with patch("huggingface_hub.hf_hub_download", side_effect=missing):
            with self.assertRaisesRegex(RuntimeError, "online-model.py --cloning"):
                Converter()
        self.assertTrue(calls)
        self.assertTrue(all(call["local_files_only"] for call in calls))

    def test_supertonic_also_requires_explicit_installation(self):
        import io
        from engines.supertonic3 import sidecar
        with patch.dict(os.environ, {"OMNIVOICE_STUDIO_LITE": "1"}), \
             patch.object(sidecar, "_tts", None), \
             patch("huggingface_hub.snapshot_download", side_effect=FileNotFoundError("empty")) as download:
            with self.assertRaises(FileNotFoundError):
                sidecar._load_tts(io.BytesIO())
        self.assertTrue(download.call_args.kwargs["local_files_only"])
        self.assertIn("onnx/*", download.call_args.kwargs["allow_patterns"])

    def test_hosted_onnx_sessions_respect_the_cpu_thread_budget(self):
        import io
        from engines.supertonic3 import sidecar
        with patch.dict(os.environ, {"OMNIVOICE_STUDIO_LITE": "1", "SUPERTONIC_INTRA_OP_THREADS": "2", "SUPERTONIC_INTER_OP_THREADS": "1"}), \
             patch.object(sidecar, "_tts", None), \
             patch("huggingface_hub.snapshot_download", return_value="/cached/model"), \
             patch("supertonic.TTS") as tts:
            sidecar._load_tts(io.BytesIO())
        self.assertEqual(tts.call_args.kwargs["intra_op_num_threads"], 2)
        self.assertEqual(tts.call_args.kwargs["inter_op_num_threads"], 1)
        self.assertFalse(tts.call_args.kwargs["auto_download"])

    def test_long_reference_is_rejected_with_a_bounded_decode(self):
        import tempfile
        import wave
        from engines.openvoice_v2.converter import _load_reference
        from services.ffmpeg_utils import find_ffmpeg
        if not find_ffmpeg():
            self.skipTest("ffmpeg is part of the Docker runtime")
        with tempfile.NamedTemporaryFile(suffix=".wav") as clip:
            with wave.open(clip.name, "wb") as writer:
                writer.setnchannels(1)
                writer.setsampwidth(2)
                writer.setframerate(16000)
                writer.writeframes(b"\0\0" * (16000 * 31))
            with self.assertRaisesRegex(ValueError, "1 and 30 seconds"):
                _load_reference(clip.name, 22050)

    def test_reference_audio_changes_the_engine_output(self):
        import torch
        from engines.supertonic3.backend import Supertonic3Backend
        from services.subprocess_backend import SubprocessBackend
        base, cloned = torch.zeros(1, 4000), torch.ones(1, 4000)
        with patch.dict(os.environ, {"OMNIVOICE_STUDIO_LITE": "1"}), \
             patch.object(SubprocessBackend, "generate", return_value=base), \
             patch("engines.openvoice_v2.converter.convert", return_value=cloned) as convert:
            backend = Supertonic3Backend()
            actual = backend.generate("Halo dunia", language="id", ref_audio="sample.wav")
            self.assertIs(actual, cloned)
            convert.assert_called_once_with(base, backend.sample_rate, "sample.wav")
            convert.reset_mock()
            self.assertIs(backend.generate("Hello world", language="en"), base)
            convert.assert_not_called()
            with self.assertRaisesRegex(ValueError, "Indonesian and English"):
                backend.generate("Bonjour", language="fr")

    def test_speech_api_does_not_advertise_transcription_models(self):
        from api.routers.openai_compat import _model_list
        with patch.dict(os.environ, {"OMNIVOICE_STUDIO_LITE": "1"}), \
             patch("services.tts_backend.list_backends", return_value=[]):
            models = _model_list()
        self.assertTrue(models)
        self.assertTrue(all(model["voicestudio"]["kind"] == "tts" for model in models))

    def test_story_renderer_is_retained_without_book_import(self):
        from api.routers.story_render import router
        paths = {route.path for route in router.routes}
        self.assertIn("/longform/render", paths)
        self.assertIn("/audiobook/resume/{job_id}", paths)
        self.assertNotIn("/audiobook/import", paths)
        self.assertTrue(all(route.dependencies for route in router.routes))

    def test_routes_and_models_do_not_import_removed_workspaces(self):
        from core.studio_scope import ROUTERS
        self.assertTrue({"generation", "profiles", "stories", "openai_compat"}.issubset(ROUTERS))
        self.assertFalse({"dub_core", "dictation", "calls", "mcp_bindings", "cloud_sync"}.intersection(ROUTERS))


if __name__ == "__main__":
    unittest.main()
