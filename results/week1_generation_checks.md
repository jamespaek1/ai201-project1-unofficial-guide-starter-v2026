# Week 1 generation checks

## Environment

`python test.py` completed with **10 passed, 0 failed, 0 warnings, 0 skipped**
after the local key was configured. Python 3.12.14, all seven pinned dependency
imports, real 384-dimensional MiniLM embeddings, and a Chroma cosine round trip
passed. `gemini-3.5-flash-lite` replied `Ready.` to the live API check.

The local sandbox required an alternate writable temporary directory for
CoreML compilation. Embedding weights were cached under the task's work
folder. These are local runtime accommodations; the repository's model,
embedding code, and RUNNING.md were unchanged.

## Current pipeline: successful sample

The current `default` index answered the Morrow House wash/dry/payment question
with caching disabled: $1.50 wash, $1.25 dry, coin or card, with a supporting
source filename. The original sample used 595 tokens (533 input, 62 output).
A second fresh request confirmed the same facts and citations and used 591
tokens (533 input, 58 output).

Exact outputs are in `week1_sample_answer.json` and `week1_sample_recheck.json`.
These are sample and confirmation calls, not the three-run Week 2 evaluation.

## Additional starter-variant check: permission error

The preserved 88-chunk `starter` index was queried with:

```bash
python app.py --variant starter ask "is the housing lottery random?" --threshold 0.6
```

Retrieval passed the original cutoff (best distance 0.254, cutoff 0.6), but the
model request returned this error on the initial attempt and one retry:

```text
ClientError: 403 PERMISSION_DENIED. {'error': {'code': 403, 'message': 'The caller does not have permission', 'status': 'PERMISSION_DENIED'}}
```

The subsequent current-pipeline Morrow House request succeeded with the same
configured key and model. The reason for these permission errors is not
established; they are not counted as answers or hidden as successful checks.
Google's [API error reference](https://ai.google.dev/gemini-api/docs/api-errors)
identifies 403 as a permission problem and recommends checking key permissions
and project access. No access settings or credentials were changed to work
around it. If it recurs, inspect the project's access in AI Studio before
running the Week 2 evaluation.
