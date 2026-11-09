"""Bounded long-form work must preserve the complete narration and cast."""
from dataclasses import asdict

from services.audiobook import AudiobookPlan, Chapter, ExpressiveOptions, Span


def test_long_chapter_is_bounded_and_resume_plan_is_idempotent():
    from services.hosted_narration import bounded_plan
    text = 'Halo dunia. Selamat datang di channel saya. ' * 900
    original = AudiobookPlan([Chapter('Cerita', [Span('alice', text, 23000, 0.8, 'paragraph', 'calm'),
                                               Span('bob', 'Hello again.', 1000, 1.2)])])
    before = asdict(original)
    plan = bounded_plan(original, ExpressiveOptions())
    assert len(plan.chapters) > 20
    assert all(chapter.char_count <= 960 for chapter in plan.chapters)
    assert all(sum(span.pause_ms_after for span in chapter.spans) <= 20000 for chapter in plan.chapters)
    spans = [span for chapter in plan.chapters for span in chapter.spans]
    assert ' '.join(span.text for span in spans if span.voice_id == 'alice').split() == text.split()
    assert sum(span.pause_ms_after for span in spans) == 24000
    assert all(span.speed == 0.8 and span.emotion == 'calm' for span in spans if span.text and span.voice_id == 'alice')
    spoken = [span for span in spans if span.text]
    assert spoken[-1].voice_id == 'bob' and spoken[-1].speed == 1.2
    assert all(len(span.text) <= 240 for span in spans)
    assert asdict(bounded_plan(plan, ExpressiveOptions())) == asdict(plan)
    assert asdict(original) == before


def test_boundary_keeps_the_gap_between_lines():
    from services.hosted_narration import bounded_plan
    spans = [Span('v', 'word ' * 40) for _ in range(12)]
    plan = bounded_plan(AudiobookPlan([Chapter('A', spans)]), ExpressiveOptions(line_gap_ms=250))
    assert len(plan.chapters) > 1
    assert all(chapter.spans[-1].pause_ms_after == 250 for chapter in plan.chapters[:-1])


def test_converter_bounds_model_windows_and_keeps_every_sample(monkeypatch):
    import torch
    from engines.openvoice_v2 import converter
    instance = object.__new__(converter.Converter)
    instance.rate = 100
    calls = []
    embeddings = []

    class Model:
        def voice_conversion(self, spec, lengths, **kwargs):
            calls.append(spec.shape[-1])
            return (spec,)

    instance.model = Model()
    instance._spectrogram = lambda audio: audio.unsqueeze(1)
    instance._embedding = lambda audio: embeddings.append(audio.shape[-1]) or torch.ones(1, 1, 1)
    monkeypatch.setattr(converter, '_load_reference', lambda path, rate: torch.ones(1, 100))
    source = torch.sin(torch.arange(3000).float() / 10).unsqueeze(0)
    result = instance.convert(source, 100, 'reference.wav')
    assert len(calls) >= 4
    assert max(calls) <= 840  # 8 seconds + 0.2 seconds of context on each side.
    assert max(embeddings) <= 500
    assert torch.equal(result, source)


def test_thirty_minute_disk_render_resumes_without_synthesis(tmp_path, monkeypatch):
    """Real WAV caches/mux, stub inference: test duration and bounded resume work."""
    import json
    import shutil
    import subprocess
    import pytest
    import torch
    from api.routers.audiobook import _render_chapter_cached
    from services.hosted_narration import bounded_plan
    from services.longform_render import build_concat_list
    from services import watermark

    ffmpeg, ffprobe = shutil.which('ffmpeg'), shutil.which('ffprobe')
    if not ffmpeg or not ffprobe:
        pytest.skip('ffmpeg/ffprobe required for real long-form mux')
    monkeypatch.setenv('OMNIVOICE_STUDIO_LITE', '1')
    marks = []
    monkeypatch.setattr(watermark, 'mark_synthetic',
                        lambda audio, rate, **kw: marks.append(audio.numel()) or audio)
    spans = [Span('voice', f'Part {index:03d}. ' + 'This is narrated text. ' * 9, join='continue')
             for index in range(120)]
    plan = bounded_plan(AudiobookPlan([Chapter('Long story', spans)]), ExpressiveOptions())
    rate, calls = 8000, []

    def synth(text, voice, speed):
        calls.append(len(text))
        return torch.full((1, rate * 15), 0.01)

    def resolve(voice):
        return {'seed': 42}

    files = []
    total = 0
    for chapter in plan.chapters:
        path, duration, cached, _ = _render_chapter_cached(
            chapter, synth, rate, 'test-engine', resolve, str(tmp_path / 'cache'))
        assert not cached
        files.append(path)
        total += duration
    assert total == 1800
    assert len(calls) == 120 and max(calls) <= 240
    assert max(marks) <= rate * 60

    def no_synthesis(*args, **kwargs):
        raise AssertionError('Completed parts must be reused after interruption')

    for chapter in plan.chapters:
        _, _, cached, _ = _render_chapter_cached(
            chapter, no_synthesis, rate, 'test-engine', resolve, str(tmp_path / 'cache'))
        assert cached
    concat = tmp_path / 'concat.txt'
    concat.write_text(build_concat_list(files))
    output = tmp_path / 'thirty-minutes.mp3'
    subprocess.run([ffmpeg, '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(concat),
                    '-c:a', 'libmp3lame', '-b:a', '32k', str(output)], check=True, timeout=60)
    probe = subprocess.run([ffprobe, '-v', 'error', '-show_entries', 'format=duration',
                            '-of', 'json', str(output)], capture_output=True, text=True, check=True)
    assert abs(float(json.loads(probe.stdout)['format']['duration']) - 1800) < 0.3
