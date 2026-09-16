"""Compare both versions under the SAME scripted outage; never calls an API.

These controlled results are separate from real Gemini acceptance evidence.
Run: python tools/check_retry_comparison.py
"""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from google.genai.errors import ServerError
import config
import generate


def main():
    baseline = ModuleType("baseline_generate")
    source = subprocess.check_output(["git", "show", "0b4e4e6:generate.py"], text=True)
    exec(compile(source, "0b4e4e6:generate.py", "exec"), baseline.__dict__)
    rows = []
    for name, module in (("before", baseline), ("after", generate)):
        client = MagicMock()
        client.models.generate_content.side_effect = [
            ServerError(503, {"error": {"code": 503, "message": "Scripted temporary outage", "status": "UNAVAILABLE"}}),
            SimpleNamespace(text="CONTROLLED SUCCESS — not a real model answer", usage_metadata=None),
        ]
        log = io.StringIO()
        with patch.object(module, "_get_client", return_value=client), patch.object(module.time, "sleep") as sleep, contextlib.redirect_stderr(log):
            try:
                answer = module.generate("Controlled prompt", system="Controlled instruction", cache=False)
                error = None
            except Exception as exc:
                answer, error = None, f"{type(exc).__name__}: {exc}"
        rows.append({"configuration": name, "answer": answer, "error": error,
                     "attempts": client.models.generate_content.call_count,
                     "requested_delays_seconds": [c.args[0] for c in sleep.call_args_list],
                     "console": log.getvalue()})
    assert rows[0]["answer"] is None and rows[0]["attempts"] == 1
    assert rows[1]["answer"] is not None and rows[1]["attempts"] == 2
    output = {"kind": "CONTROLLED FAILURE INJECTION; no live model calls",
              "sequence": "HTTP 503, then a scripted successful response",
              "baseline_commit": "0b4e4e6", "results": rows}
    path = config.RESULTS_DIR / "week2_controlled_retry_comparison.json"
    path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
