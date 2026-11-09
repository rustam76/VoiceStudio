"""Bound work units for the existing hosted Stories cache and resume renderer."""
from dataclasses import replace

from services.audiobook import AudiobookPlan, Chapter, ExpressiveOptions, Span, _JoinPolicy
from services.chunked_tts import split_text_into_chunks

MAX_TEXT_CHARS = 240
MAX_PART_CHARS = 960
MAX_PART_PAUSE_MS = 20000


def bounded_plan(plan: AudiobookPlan, opts: ExpressiveOptions) -> AudiobookPlan:
    """Materialize gaps and split large chapters before they allocate audio.

    Only hosted rendering uses this. Parts remain normal chapters, so the
    existing disk cache, cancellation, progress and durable resume all apply.
    """
    chapters = []
    policy = _JoinPolicy(opts.line_gap_ms, opts.paragraph_gap_ms)
    for chapter in plan.chapters:
        pieces = []

        def silence(milliseconds):
            while milliseconds > 0:
                length = min(milliseconds, 10000)
                pieces.append(Span(None, '', length, join='continue'))
                milliseconds -= length

        pending_gap = 0
        for span in chapter.spans:
            if span.text.strip():
                silence(pending_gap)
                paragraphs = policy.pieces(span.text)
                for index, paragraph in enumerate(paragraphs):
                    if index:
                        silence(opts.paragraph_gap_ms)
                    pieces.extend(replace(span, text=text, pause_ms_after=0, join='continue')
                                  for text in split_text_into_chunks(paragraph, MAX_TEXT_CHARS))
                pending_gap = policy.silence_after(span)
            if span.pause_ms_after > 0:
                pending_gap = 0
                silence(span.pause_ms_after)

        parts, current = [], []
        characters = pauses = 0
        for span in pieces:
            if current and (characters + len(span.text) > MAX_PART_CHARS
                            or pauses + span.pause_ms_after > MAX_PART_PAUSE_MS):
                parts.append(current)
                current, characters, pauses = [], 0, 0
            current.append(span)
            characters += len(span.text)
            pauses += span.pause_ms_after
        if current:
            parts.append(current)
        chapters.extend(Chapter(chapter.title if len(parts) == 1 else f'{chapter.title} · {i + 1}', spans)
                        for i, spans in enumerate(parts))
    return AudiobookPlan(chapters)
