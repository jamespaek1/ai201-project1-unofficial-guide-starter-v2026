# Milestone 1: corpus inspection

Corpus: `campus_life`. These are fictional course documents, not current university policies.

88 documents, 27,908 characters, ~317 characters per document
88 chunks, 317 characters on average (shortest 178, longest 549), produced by chunker.py::fallback_split

The unchanged starter keeps each short post whole. The corpus is already plain
text; ingest.py normalizes whitespace and keeps filenames for attribution.

Documents read before choosing a chunking strategy:
- `dining_kestrel_commons.txt`: queue times and food advice in one paragraph,
  opening hours and payment in another. A paragraph is a useful topic boundary.
- `course_cs_210.txt`: assessment, workload, and lab advice are separate paragraphs.
- `housing_morrow_house_laundry.txt`: exact prices/payment followed by timing advice.
- `admin_housing_lottery.txt`: one paragraph; the random-number claim needs its
  year-group qualifications, so it should stay together.

Across 88 cleaned posts, lengths are 178–549 characters, averaging 317. Body
paragraphs have a median length of 112 characters; the longest is the 373-character
housing lottery explanation. Every source begins with a short identifying title.

The starter index was built with the real all-MiniLM-L6-v2 ONNX model in a separate
`starter` variant: 88 chunks stored. Generation is pending a GEMINI_API_KEY.

## Follow-up after configuring the key

The current pipeline now has a real generated sample with citations, recorded
in `week1_sample_answer.json`. A later attempt to obtain an answer from the
preserved starter index reached the model but returned a provider permission
error; see `week1_generation_checks.md`. This follow-up happened after the
chunker implementation and is not presented as an earlier milestone run.
