"""Lazy-loaded Whisper transcription."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from src.settings import Settings

LOG = logging.getLogger(__name__)


@lru_cache(maxsize=2)
def _load_model(name: str):
    import whisper

    LOG.info("Loading Whisper model '%s'", name)
    return whisper.load_model(name)


def transcribe_audio(filename: str, *, settings: Settings | None = None) -> str:
    settings = settings or Settings.from_env()
    path = Path(filename)
    if not path.is_file():
        raise FileNotFoundError(f"Audio recording not found: {path}")
    try:
        result = _load_model(settings.whisper_model).transcribe(str(path))
    except Exception as exc:
        raise RuntimeError(f"Speech transcription failed: {exc}") from exc
    return str(result.get("text", "")).strip()
