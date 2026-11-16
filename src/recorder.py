"""Microphone capture with voice activity detection and bounded duration."""

from __future__ import annotations

import logging
import tempfile
import threading
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

from src.settings import Settings

LOG = logging.getLogger(__name__)


def record_audio(*, settings: Settings | None = None) -> str | None:
    settings = settings or Settings.from_env()
    chunks: list[np.ndarray] = []
    speech_started = threading.Event()
    silence_started: float | None = None

    def callback(indata, frames, time_info, status):
        nonlocal silence_started
        if status:
            LOG.warning("Audio input status: %s", status)
        chunks.append(indata.copy())
        volume = float(np.sqrt(np.mean(np.square(indata.astype(np.float32)))))
        if volume >= settings.silence_threshold:
            speech_started.set()
            silence_started = None
        elif speech_started.is_set() and silence_started is None:
            silence_started = time.monotonic()

    started = time.monotonic()
    print("\nListening…")
    try:
        with sd.InputStream(samplerate=settings.sample_rate, channels=settings.channels, dtype="int16", callback=callback):
            while time.monotonic() - started < settings.max_recording_seconds:
                if speech_started.is_set() and silence_started is not None and time.monotonic() - silence_started >= settings.silence_duration:
                    break
                time.sleep(0.05)
    except Exception as exc:
        raise RuntimeError(f"Could not record audio; check microphone permissions and input device: {exc}") from exc

    if not chunks or not speech_started.is_set():
        return None
    audio = np.concatenate(chunks, axis=0)
    handle = tempfile.NamedTemporaryFile(prefix="voice-assistant-", suffix=".wav", delete=False)
    filename = handle.name
    handle.close()
    try:
        write(filename, settings.sample_rate, audio)
    except Exception:
        Path(filename).unlink(missing_ok=True)
        raise
    return filename
