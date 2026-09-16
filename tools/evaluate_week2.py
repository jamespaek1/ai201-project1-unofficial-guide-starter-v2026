"""Capture the unmodified run_eval pipeline, including chunks and API failures.

Usage: python tools/evaluate_week2.py --label before
       python tools/evaluate_week2.py --label after

Calls run_eval.main and the original run_once. The observation wrappers do not
change retrieval, prompts, model settings, cache=False, or the gate. A provider
exception is recorded as an error (never a generated answer), allowing the
remaining scheduled trials to finish instead of losing the entire run log.
"""

import contextlib
from dataclasses import asdict
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app
import chunker
import config
import gate
import generate
from ingest import load_documents
import run_eval
import store


def main():
    label = sys.argv[sys.argv.index("--label") + 1] if "--label" in sys.argv else "evaluation"
    if label not in {"before", "after"}:
        raise SystemExit("Use --label before or --label after")
    path = config.RESULTS_DIR / f"week2_{label}_evidence.json"
    if path.exists():
        raise SystemExit(f"Refusing to overwrite evidence: {path}")
    assert not __import__("os").environ.get("AI201_FAKE_EMBEDDINGS"), "Real embeddings required"
    documents = load_documents(config.CORPUS)
    chunks = chunker.split_documents(documents)
    indexed = store._client().get_collection(config.collection_name()).get()
    assert dict(zip(indexed["ids"], indexed["documents"])) == {c.label: c.text for c in chunks}, "Index does not match the current chunker"
    step = max(len(chunks) // 5, 1)
    data = {
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "label": label,
        "model": config.MODEL,
        "embedding_model": config.EMBEDDING_MODEL,
        "corpus": config.CORPUS,
        "corpus_sha256": hashlib.sha256(json.dumps([(d.source, d.text) for d in documents]).encode()).hexdigest(),
        "criteria_sha256": hashlib.sha256((config.ROOT / "criteria.md").read_bytes()).hexdigest(),
        "top_k": config.TOP_K,
        "threshold": config.THRESHOLD,
        "chunk_size": config.CHUNK_SIZE,
        "cache": False,
        "index_verified_against_chunker": True,
        "chunk_count": len(chunks),
        "sampled_chunks": [asdict(c) for c in chunks[::step][:5]],
        "trials": [],
        "out_of_scope": [],
    }
    def save():
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    config.RESULTS_DIR.mkdir(exist_ok=True)
    save()
    original_search = store.search
    original_once = run_eval.run_once
    last_results = None

    def observed_search(*args, **kwargs):
        nonlocal last_results
        last_results = original_search(*args, **kwargs)
        return last_results

    def observed_once(question, top_k, threshold, corpus, variant):
        nonlocal last_results
        last_results = None
        before_calls = generate.call_count()
        entry = {"question": question, "run": 1 + sum(t["question"] == question for t in data["trials"])}
        try:
            answer, results, decision = original_once(question, top_k, threshold, corpus, variant)
            entry.update(answer=answer, error=None)
        except Exception as exc:
            # Only continue after an actual outgoing generation attempt. A broken
            # retrieval/index is an experiment setup error and must stop the run.
            if last_results is None or generate.call_count() == before_calls:
                raise
            results = last_results
            decision = gate.check(results, threshold=threshold)
            error = f"{type(exc).__name__}: {exc}"
            key = __import__("os").environ.get("GEMINI_API_KEY", "")
            if key:
                error = error.replace(key, "[REDACTED]")
            answer = "[PROVIDER ERROR — no answer generated]\n" + error
            entry.update(answer=None, error=error)
        entry.update(results=[asdict(r) for r in results], gate=asdict(decision),
                     model_calls=generate.call_count() - before_calls)
        data["trials"].append(entry)
        save()
        return answer, results, decision

    original_scope = run_eval.check_out_of_scope
    def observed_scope(*args, **kwargs):
        before_calls = generate.call_count()
        rows = original_scope(*args, **kwargs)
        data["out_of_scope"] = rows
        data["out_of_scope_model_calls"] = generate.call_count() - before_calls
        save()
        return rows

    with patch.object(store, "search", observed_search), patch.object(run_eval, "run_once", observed_once), patch.object(run_eval, "check_out_of_scope", observed_scope):
        run_eval.main()
    data.update(completed_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                usage=generate.usage(), tokens=generate.token_counts())
    save()
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        app.cmd_chunks(app.build_parser().parse_args(["chunks", "-n", "5"]))
    (config.RESULTS_DIR / f"week2_{label}_chunks.txt").write_text(output.getvalue())
    print(f"Detailed evidence: {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
