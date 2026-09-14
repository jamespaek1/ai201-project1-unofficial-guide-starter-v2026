"""Record Week 1 distances without calling the answer-generation model.

Run from the repository root: python tools/calibrate.py
"""

import contextlib
import io
import json
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app
import config
from questions import OUT_OF_SCOPE, answered
from store import search


def main():
    rows = []
    output = io.StringIO()
    questions = [(q["question"], True) for q in answered()]
    questions += [(question, False) for question in OUT_OF_SCOPE]
    for question, in_corpus in questions:
        results = search(question)
        rows.append({
            "question": question,
            "in_corpus": in_corpus,
            "best_distance": min(r.distance for r in results),
            "results": [asdict(r) for r in results],
        })
        with contextlib.redirect_stdout(output):
            app.cmd_retrieve(SimpleNamespace(
                question=question, top_k=config.TOP_K,
                corpus=config.CORPUS, variant="default",
            ))

    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=config.ROOT, text=True,
        ).strip(),
        "corpus": config.CORPUS,
        "embedding_model": config.EMBEDDING_MODEL,
        "chunk_size": config.CHUNK_SIZE,
        "body_overlap": config.CHUNK_OVERLAP,
        "top_k": config.TOP_K,
        "threshold_at_measurement": config.THRESHOLD,
        "rows": rows,
    }
    config.RESULTS_DIR.mkdir(exist_ok=True)
    (config.RESULTS_DIR / "week1_distances.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    (config.RESULTS_DIR / "week1_retrieval.txt").write_text(
        output.getvalue(), encoding="utf-8",
    )
    for row in rows:
        group = "IN " if row["in_corpus"] else "OUT"
        print(f"{group} {row['best_distance']:.6f}  {row['question']}")


if __name__ == "__main__":
    main()
