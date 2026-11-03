"""Bounded narration profile; upstream desktop behavior stays opt-in independent."""
import math

from fastapi import HTTPException


def generation_policy(*, text, language, engine, speed, profile_id, ref_audio,
                      instruct, design_recipe, max_chunk_chars):
    if not text.strip() or len(text) > 6000:
        raise HTTPException(422, "Text must contain 1–6000 characters.")
    from omnivoice.utils.text import parse_pause_markers
    segments = parse_pause_markers(text)
    if sum(pause_ms for _, pause_ms in segments) > 30000:
        raise HTTPException(422, "Total explicit pauses must not exceed 30 seconds.")
    if not any(span.strip() for span, _ in segments):
        raise HTTPException(422, "Text must contain speech, not only pause markers.")
    if engine not in (None, "", "supertonic3"):
        raise HTTPException(422, "Only supertonic3 is enabled in VoiceStudio Online.")
    if not math.isfinite(speed) or not 0.7 <= speed <= 2.0:
        raise HTTPException(422, "Speed must be between 0.7 and 2.0.")
    if profile_id or ref_audio is not None or instruct or design_recipe:
        raise HTTPException(422, "Cloning and voice design are disabled in VoiceStudio Online.")
    if not 100 <= max_chunk_chars <= 1000:
        raise HTTPException(422, "Chunk size must be between 100 and 1000 characters.")
    return language or "id"
