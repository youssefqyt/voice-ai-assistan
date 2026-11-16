"""Local-first voice assistant entry point."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.llm import ask_ai
from src.settings import Settings
from src.text_to_speech import speak

LOG = logging.getLogger("voice_assistant")


def run(*, text_mode: bool = False, settings: Settings | None = None) -> int:
    settings = settings or Settings.from_env()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    recorder = transcriber = None
    if not text_mode:
        from src.recorder import record_audio
        from src.speech_to_text import transcribe_audio
        recorder, transcriber = record_audio, transcribe_audio

    print("Voice AI Assistant — local speech recognition, Ollama, and system TTS")
    print("Type or say 'exit' to stop.")
    while True:
        try:
            if text_mode:
                question = input("\nYou: ").strip()
                if not question:
                    continue
            else:
                filename = recorder(settings=settings)
                if filename is None:
                    print("No speech detected. Try again, or press Ctrl+C to stop.")
                    continue
                try:
                    print("Transcribing…")
                    question = transcriber(filename, settings=settings)
                finally:
                    Path(filename).unlink(missing_ok=True)
                if not question:
                    print("No speech detected. Try again.")
                    continue
                print(f"\nYou: {question}")

            if question.casefold() in {"exit", "quit", "stop"}:
                print("Goodbye!")
                if not text_mode:
                    speak("Goodbye!", settings=settings)
                return 0
            answer = ask_ai(question, settings=settings)
            print(f"\nAssistant: {answer}")
            if not text_mode:
                speak(answer, settings=settings)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            return 0
        except Exception as exc:
            LOG.exception("Turn failed")
            print(f"I couldn't complete that turn: {exc}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="A local-first voice assistant")
    parser.add_argument("--text", action="store_true", help="Use typed input/output without microphone or TTS")
    return run(text_mode=parser.parse_args().text)


if __name__ == "__main__":
    raise SystemExit(main())
