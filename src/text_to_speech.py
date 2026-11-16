"""System speech synthesis."""

from __future__ import annotations


def speak(text: str, *, settings=None) -> None:
    if not text.strip():
        return
    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.setProperty("rate", 170)
        engine.setProperty("volume", 1.0)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as exc:
        raise RuntimeError(f"Text-to-speech failed: {exc}") from exc
