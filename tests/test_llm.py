import unittest
from unittest.mock import Mock, patch

from src import llm
from src.settings import Settings


class LlmTests(unittest.TestCase):
    def setUp(self):
        llm.reset_conversation()

    def test_uses_chat_api_and_keeps_bounded_context(self):
        response = Mock()
        response.json.return_value = {"message": {"content": "Hello there."}}
        settings = Settings(conversation_turns=1)
        with patch("src.llm.requests.post", return_value=response) as post:
            self.assertEqual(llm.ask_ai("Hi", settings=settings), "Hello there.")
            self.assertEqual(llm.ask_ai("Again", settings=settings), "Hello there.")
        self.assertEqual(post.call_args.kwargs["timeout"], 120.0)
        messages = post.call_args.kwargs["json"]["messages"]
        self.assertEqual([message["role"] for message in messages], ["system", "user", "assistant", "user"])
        self.assertEqual(len(llm._conversation), 2)

    def test_empty_question_does_not_call_service(self):
        with patch("src.llm.requests.post") as post:
            with self.assertRaisesRegex(ValueError, "empty"):
                llm.ask_ai("  ")
        post.assert_not_called()

    def test_service_failure_has_actionable_message(self):
        with patch("src.llm.requests.post", side_effect=__import__("requests").ConnectionError("offline")):
            with self.assertRaisesRegex(RuntimeError, "Start Ollama"):
                llm.ask_ai("Hi")


if __name__ == "__main__":
    unittest.main()
