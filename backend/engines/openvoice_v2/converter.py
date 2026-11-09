"""CPU tone-colour cloning; adapted from OpenVoice (see vendor/LICENSE).

Only explicit model installation may contact the Hub. A reference is decoded by
our bounded audio loader, not the upstream ASR/VAD/transcription pipeline.
"""
from __future__ import annotations

import json
import math
import subprocess
import threading
from pathlib import Path

import numpy as np

import torch
import torch.nn.functional as F

MODEL_REPO_ID = "myshell-ai/OpenVoiceV2"
PINNED_REVISION_SHA = "f36e7edfe1684461a8343844af60babc2efbb727"
CONVERTER_FILES = ("converter/config.json", "converter/checkpoint.pth")


def _load_reference(path: str, rate: int) -> torch.Tensor:
    """Decode at most 31 seconds; reject long/empty clips without full-file loads."""
    from services.ffmpeg_utils import find_ffmpeg, local_inputs_only

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        raise RuntimeError("Voice cloning needs ffmpeg; install the server runtime")
    result = subprocess.run(local_inputs_only([
        ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-i", path,
        "-map", "0:a:0", "-t", "31", "-ac", "1", "-ar", str(rate),
        "-f", "f32le", "pipe:1",
    ]), capture_output=True, timeout=30, check=False)
    if result.returncode:
        raise ValueError("Reference audio could not be decoded")
    samples = np.frombuffer(result.stdout, dtype="<f4").copy()
    if not rate <= samples.size <= rate * 30:
        raise ValueError("Use a clear voice reference between 1 and 30 seconds")
    target = torch.from_numpy(samples).unsqueeze(0)
    if not torch.isfinite(target).all() or target.square().mean() < 1e-8:
        raise ValueError("Reference audio is silent or invalid")
    return target


class Converter:
    def __init__(self):
        from huggingface_hub import hf_hub_download
        from .vendor.models import SynthesizerTrn

        try:
            paths = [hf_hub_download(MODEL_REPO_ID, name, revision=PINNED_REVISION_SHA,
                                     local_files_only=True) for name in CONVERTER_FILES]
        except Exception as exc:
            raise RuntimeError("OpenVoice V2 is not installed. Run: "
                               "HF_HUB_OFFLINE=0 python /app/scripts/online-model.py --cloning") from exc
        self.config = json.loads(Path(paths[0]).read_text(encoding="utf-8"))
        data = self.config["data"]
        self.rate = data["sampling_rate"]
        self.model = SynthesizerTrn(len(self.config.get("symbols", [])),
                                   data["filter_length"] // 2 + 1,
                                   n_speakers=data["n_speakers"], **self.config["model"]).cpu().eval()
        checkpoint = torch.load(paths[1], map_location="cpu", weights_only=True)
        # An incomplete or incompatible checkpoint must never produce a fake clone.
        self.model.load_state_dict(checkpoint["model"], strict=True)

    def _spectrogram(self, audio: torch.Tensor) -> torch.Tensor:
        data = self.config["data"]
        n_fft, hop, win = data["filter_length"], data["hop_length"], data["win_length"]
        pad = (n_fft - hop) // 2
        audio = F.pad(audio.unsqueeze(1), (pad, pad), mode="reflect").squeeze(1)
        spec = torch.stft(audio, n_fft, hop_length=hop, win_length=win,
                          window=torch.hann_window(win), center=False, return_complex=True)
        return (spec.abs().square() + 1e-6).sqrt()

    def _embedding(self, audio: torch.Tensor) -> torch.Tensor:
        return self.model.ref_enc(self._spectrogram(audio).transpose(1, 2)).unsqueeze(-1)

    @torch.inference_mode()
    def convert(self, source: torch.Tensor, source_rate: int, reference: str) -> torch.Tensor:
        from scipy.signal import resample_poly

        target_audio = _load_reference(reference, self.rate)

        def mono_at_rate(wave, rate):
            wave = wave.detach().cpu().float().reshape(wave.shape[0], -1).mean(0)
            if not wave.numel() or not torch.isfinite(wave).all():
                raise ValueError("Reference audio is empty or invalid")
            if rate != self.rate:
                divisor = math.gcd(rate, self.rate)
                wave = torch.from_numpy(resample_poly(wave.numpy(), self.rate // divisor,
                                                     rate // divisor).copy())
            return wave.unsqueeze(0)

        source = source.detach().cpu().float()
        if source.ndim == 1:
            source = source.unsqueeze(0)
        if source.ndim != 2 or not source.numel() or not torch.isfinite(source).all():
            raise ValueError("Source audio is empty or invalid")
        # Speaker identity is shared by all windows; never encode a whole
        # narration just to identify the source voice.
        source_identity = mono_at_rate(source[:, :source_rate * 5], source_rate)
        source_se = self._embedding(source_identity)
        target_se = self._embedding(target_audio)
        samples = source.shape[-1]
        output = torch.empty((1, samples), dtype=torch.float32)
        window_size = source_rate * 8
        context = max(1, source_rate // 5)
        for start in range(0, samples, window_size):
            end = min(samples, start + window_size)
            left, right = max(0, start - context), min(samples, end + context)
            source_audio = mono_at_rate(source[:, left:right], source_rate)
            spec = self._spectrogram(source_audio)
            converted = self.model.voice_conversion(
                spec, torch.LongTensor([spec.shape[-1]]),
                sid_src=source_se, sid_tgt=target_se, tau=0.3,
            )[0][0].cpu().float()
            if self.rate != source_rate:
                divisor = math.gcd(self.rate, source_rate)
                converted = torch.from_numpy(resample_poly(
                    converted.numpy(), source_rate // divisor, self.rate // divisor, axis=-1,
                ).copy())
            if not converted.numel() or not torch.isfinite(converted).all():
                raise RuntimeError("OpenVoice produced invalid audio")
            # Overlapping context is discarded, not appended twice. Keeping the
            # exact original sample count prevents timing drift on long stories.
            offset, count = start - left, end - start
            core = converted[..., offset:offset + count]
            output[:, start:end] = F.pad(core, (0, count - core.shape[-1]))
        converted = output
        # The generation router applies mark_synthetic to the FINAL converted take.
        return converted


_lock = threading.Lock()
_converter: Converter | None = None


def convert(source: torch.Tensor, sample_rate: int, reference: str) -> torch.Tensor:
    global _converter
    with _lock:
        if _converter is None:
            _converter = Converter()
        return _converter.convert(source, sample_rate, reference)


def unload() -> None:
    global _converter
    with _lock:
        _converter = None
