"""Hosted narration studio: Indonesian/English, profiles, Stories and REST API."""
import os


def enabled() -> bool:
    return os.environ.get("OMNIVOICE_STUDIO_LITE", "").lower() in {"1", "true", "yes"}


ROUTERS = (
    "system", "profiles", "profile_images", "exports", "generation", "engines",
    "stories", "story_render", "setup", "watermark", "events", "openai_compat", "tts_stream",
    "personas", "longform_jobs", "pronunciation", "settings", "auth",
)
