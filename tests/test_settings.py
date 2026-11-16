import unittest
from unittest.mock import patch

from src.settings import Settings


class SettingsTests(unittest.TestCase):
    def test_defaults(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(Settings.from_env().ollama_model, "llama3.2:3b")

    def test_reads_environment(self):
        with patch.dict("os.environ", {"OLLAMA_URL": "http://localhost:1234/", "CONVERSATION_TURNS": "4"}, clear=True):
            settings = Settings.from_env()
        self.assertEqual(settings.ollama_url, "http://localhost:1234")
        self.assertEqual(settings.conversation_turns, 4)

    def test_rejects_invalid_audio_configuration(self):
        with patch.dict("os.environ", {"SAMPLE_RATE": "0"}, clear=True):
            with self.assertRaisesRegex(ValueError, "positive"):
                Settings.from_env()


if __name__ == "__main__":
    unittest.main()
