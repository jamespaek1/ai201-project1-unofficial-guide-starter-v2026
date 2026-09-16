"""Controlled checks of transient failure recovery, independent of live load."""

from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from google.genai.errors import ClientError, ServerError

import config
import generate


def unavailable():
    return ServerError(503, {"error": {"code": 503, "message": "Temporary high demand", "status": "UNAVAILABLE"}})


class RetryTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client_patch = patch.object(generate, "_get_client", return_value=self.client)
        self.client_patch.start()
        self.addCleanup(self.client_patch.stop)
        self.sleep_patch = patch.object(generate.time, "sleep")
        self.sleep = self.sleep_patch.start()
        self.addCleanup(self.sleep_patch.stop)
        for name, value in (("_session_calls", 0), ("_call_times", []), ("_cache_hits", 0), ("_session_prompt_tokens", 0), ("_session_output_tokens", 0)):
            p = patch.object(generate, name, value)
            p.start()
            self.addCleanup(p.stop)

    def test_503_then_success_repeats_same_uncached_request(self):
        self.client.models.generate_content.side_effect = [
            unavailable(), SimpleNamespace(text="Grounded answer", usage_metadata=None)
        ]
        with patch.object(generate, "_cache_read") as read, patch.object(generate, "_cache_write") as write:
            self.assertEqual(generate.generate("Question and documents", system="Grounding rules", cache=False), "Grounded answer")
        calls = self.client.models.generate_content.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], calls[1])
        self.assertEqual(generate.call_count(), 2)
        self.sleep.assert_called_once_with(1)
        read.assert_not_called()
        write.assert_not_called()

    def test_persistent_503_stops_at_existing_attempt_limit(self):
        self.client.models.generate_content.side_effect = unavailable()
        with self.assertRaisesRegex(RuntimeError, f"Service still unavailable after {config.MAX_RETRIES} attempts"):
            generate.generate("Question", cache=False)
        self.assertEqual(self.client.models.generate_content.call_count, config.MAX_RETRIES)
        self.assertEqual(generate.call_count(), config.MAX_RETRIES)
        self.assertEqual([c.args[0] for c in self.sleep.call_args_list], [2 ** i for i in range(config.MAX_RETRIES)])

    def test_403_is_not_retried(self):
        error = ClientError(403, {"error": {"code": 403, "message": "No permission", "status": "PERMISSION_DENIED"}})
        self.client.models.generate_content.side_effect = error
        with self.assertRaises(ClientError):
            generate.generate("Question", cache=False)
        self.assertEqual(self.client.models.generate_content.call_count, 1)
        self.sleep.assert_not_called()

    def test_existing_429_recovery_is_preserved(self):
        self.client.models.generate_content.side_effect = [
            ClientError(429, {"error": {"code": 429, "message": "Rate limit", "status": "RESOURCE_EXHAUSTED"}}),
            SimpleNamespace(text="Answer", usage_metadata=None),
        ]
        self.assertEqual(generate.generate("Question", cache=False), "Answer")
        self.assertEqual(self.client.models.generate_content.call_count, 2)


if __name__ == "__main__":
    unittest.main()
