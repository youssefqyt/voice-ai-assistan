"""Environment-based configuration with safe local defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout: float = 120.0
    whisper_model: str = "base"
    sample_rate: int = 16_000
    channels: int = 1
    silence_threshold: float = 500.0
    silence_duration: float = 1.5
    max_recording_seconds: float = 10.0
    conversation_turns: int = 12
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass  # Process environment remains fully supported without the optional loader.
        defaults = cls()
        settings = cls(
            ollama_url=os.getenv("OLLAMA_URL", defaults.ollama_url).rstrip("/"),
            ollama_model=os.getenv("OLLAMA_MODEL", defaults.ollama_model),
            ollama_timeout=float(os.getenv("OLLAMA_TIMEOUT", defaults.ollama_timeout)),
            whisper_model=os.getenv("WHISPER_MODEL", defaults.whisper_model),
            sample_rate=int(os.getenv("SAMPLE_RATE", defaults.sample_rate)),
            channels=int(os.getenv("AUDIO_CHANNELS", defaults.channels)),
            silence_threshold=float(os.getenv("SILENCE_THRESHOLD", defaults.silence_threshold)),
            silence_duration=float(os.getenv("SILENCE_DURATION", defaults.silence_duration)),
            max_recording_seconds=float(os.getenv("MAX_RECORDING_SECONDS", defaults.max_recording_seconds)),
            conversation_turns=int(os.getenv("CONVERSATION_TURNS", defaults.conversation_turns)),
            log_level=os.getenv("LOG_LEVEL", defaults.log_level).upper(),
        )
        if settings.sample_rate <= 0 or settings.channels <= 0:
            raise ValueError("SAMPLE_RATE and AUDIO_CHANNELS must be positive")
        if settings.max_recording_seconds <= 0 or settings.silence_duration <= 0:
            raise ValueError("Recording durations must be positive")
        if settings.conversation_turns < 1 or settings.ollama_timeout <= 0:
            raise ValueError("CONVERSATION_TURNS and OLLAMA_TIMEOUT must be positive")
        if not settings.ollama_model.strip() or not settings.whisper_model.strip():
            raise ValueError("OLLAMA_MODEL and WHISPER_MODEL cannot be empty")
        return settings
