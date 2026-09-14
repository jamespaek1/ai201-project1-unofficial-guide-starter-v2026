# The Unofficial Guide

James Paek · `campus_life` · Week 1

Implementation assistance: Codex. Work is being recorded as it is performed.

**Week 1:** Implementation, five acceptance criteria, and all five submission
sections are complete. The repository includes real chunk, retrieval, refusal,
and generation evidence, plus more than four milestone commits. The formal
Week 2 evaluation has not been run. AI assistance and the timing of the two
custom criteria are disclosed below and in [`criteria.md`](criteria.md).

Setup and commands: [`RUNNING.md`](RUNNING.md). That starter reference is unchanged.

---

# Week 1

## What This Does

The Unofficial Guide searches the supplied `campus_life` corpus: 88 fictional
student-life posts about housing, dining, courses, and campus services. It
answers specific questions such as how housing lottery priority works, what
Morrow House laundry costs, and when the library closes. Documents are cleaned,
split into titled paragraph chunks, embedded locally, and searched in a Chroma
cosine-distance index; a relevance gate runs before the Gemini prompt, which
instructs the model to use only retrieved documents and name its sources. Use
`python app.py index`, then `python app.py ask "your question"` after the setup
in `RUNNING.md`; configure your own `GEMINI_API_KEY` in the ignored `.env` file.

## Chunking Strategy

**Chunk size:** 350 characters as a soft target, including the repeated title.
**Overlap:** 0 body characters; repeat the source title on every chunk.

The 88 campus posts average 317 characters and range from 178 to 549. Kestrel
Commons separates queue advice from hours/prices, and CS 210 separates
assessment from workload and lab advice. I chose 350 so most brief posts stay
whole while longer posts can separate at these existing paragraph boundaries.
The housing lottery's 373-character body paragraph qualifies how priority
works for different years; keeping it whole matters more than forcing the
350-character target.

`chunker.py::split_documents` packs complete paragraphs beneath the title.
It never cuts a sentence or emits a title-only tail from a post with a body.
A single paragraph may exceed the target, explicitly preserving that thought.
There is no body overlap because complete paragraphs already retain the
sentences around a fact, and repeated body text would compete with distinct
facts in the five retrieved slots. The title repeats so a paragraph about
"the final" still identifies CS 210 when read alone.

This decision was written before implementing the replacement. The starter's
800/120 configuration made 88 chunks, because no campus post reaches 800
characters. The replacement is intended to separate longer multi-topic posts;
its retrieval quality will be evaluated rather than assumed.

Observed output: 115 chunks, 248 characters on average (shortest 91, longest 397), produced by chunker.py::split_documents. The title-inclusive maximum of
397 is the intentionally unsplit housing-lottery explanation. The shortest
chunk is 91 characters and contains a complete fact, not a sliced tail.
Seven unit tests passed, including exact body-paragraph preservation across all
88 sources. These are implementation checks, not Week 2 acceptance verdicts.

## Sample Chunks

Copied from `python app.py chunks -n 5`; raw output is in
[`results/week1_chunks.txt`](results/week1_chunks.txt).

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```text
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_cs_210_exams.txt#0` — produced by: `chunker.py::split_documents`

```text
CS 210 Data Structures — assessment

Two midterms and a final, all drawn from lecture material rather than the textbook. Midterms are curved, the final is not.

Do the labs even though they're only 10% — the exams reuse the lab problems.
```

**Chunk 3** — source: `course_phys_130.txt#1` — produced by: `chunker.py::split_documents`

```text
PHYS 130 Mechanics

The one piece of advice: the lab practical is worth 20% and almost nobody prepares for it.
```

**Chunk 4** — source: `dining_the_ridgeway_cafe_followup.txt#1` — produced by: `chunker.py::split_documents`

```text
Re: The Ridgeway Café

Also worth saying: seating is tight; about 40 seats for a building of 900. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_morrow_house.txt#0` — produced by: `chunker.py::split_documents`

```text
Morrow House — what it's actually like

Just finished a year in this building. Built 1954, partially renovated 2008. Rooms are singles and doubles, hall bathrooms.

The good: cheapest housing tier by about $900 a year, and the singles are real singles.

The bad: known damp problem on the ground floor; two rooms were taken offline in 2024.
```

## Sample Answer

**Question:** What are the separate wash and dry prices in Morrow House, and
which payment methods work?

**Answer:** Actual output from `app.py::_ask_one`, with the answer generated
by `generate.py::answer_from_chunks` using `gemini-3.5-flash-lite`. Caching was
disabled, so this was one real model call.

```text
(best distance 0.252, cutoff 0.65)

In Morrow House, the laundry costs $1.50 to wash and $1.25 to dry, and you can pay using either coin or card.

Source: `housing_morrow_house_laundry.txt` (also found in `housing_morrow_house.txt`)

Sources retrieved: housing_calder_annexe.txt, housing_innisfree_hall_laundry.txt, housing_morrow_house.txt, housing_morrow_house_laundry.txt, housing_old_brewhouse_laundry.txt

1 model calls this session, 595 tokens (533 in, 62 out)
```

The cited laundry post confirms all three details: $1.50 per wash, $1.25 per
dry, and coin or card payment. The answer correctly uses Morrow House's prices
even though the retrieved set also includes other residences.

Saved evidence: [`results/week1_sample_answer.txt`](results/week1_sample_answer.txt)
and the exact captured stdout in
[`results/week1_sample_answer.json`](results/week1_sample_answer.json).

A second uncached sample confirmed the same facts and sources. Two additional
housing-lottery requests against the saved starter index returned a provider
403 permission error, while the current Morrow House pipeline still worked.
This limitation and the environment check are recorded in
[`results/week1_generation_checks.md`](results/week1_generation_checks.md).

**My relevance cutoff:** `THRESHOLD = 0.65` in `config.py`.

Measured with the real `all-MiniLM-L6-v2` embedding model and cosine distance,
using 115 custom chunks. In-corpus best distances range from 0.191651 to
0.470400; out-of-corpus distances range from 0.824593 to 0.923117. The gap is
0.354194 wide. Its midpoint is 0.647496, so 0.65 leaves space on both sides.
The gate admits a question only when its best distance is strictly below 0.65.
A lower cutoff of 0.30 would wrongly refuse the library-hours question; 0.90
would admit four of these five unrelated questions.

| Question | In corpus? | Best distance |
|---|---|---|
| How does housing lottery priority differ for rising sophomores versus juniors and seniors? | Yes | 0.191651 |
| What are the separate wash and dry prices in Morrow House, and which payment methods work? | Yes | 0.252256 |
| How long is the Kestrel Commons wait between 12:15 and 1:00, and before 11:45? | Yes | 0.229261 |
| In CS 210, are the midterms and final curved, and what material are the exams drawn from? | Yes | 0.211586 |
| When does the library close during term versus reading week? | Yes | 0.470400 |
| What is the capital of Mongolia? | No | 0.824593 |
| How do I change the oil in a diesel engine? | No | 0.923117 |
| Who won the 1994 World Cup? | No | 0.885860 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.848693 |
| How do I write a for loop in Rust? | No | 0.863514 |

Measured by `tools/calibrate.py::main` using `store.py::search`. Full retrieved
text is in [`results/week1_distances.json`](results/week1_distances.json), and
verbatim `app.py::cmd_retrieve` output is in
[`results/week1_retrieval.txt`](results/week1_retrieval.txt). That initial
measurement used the starter's 0.6 cutoff; the measured distances justified
changing the cutoff to 0.65 afterward.

**Top-k:** 5. For Kestrel Commons, the follow-up at rank 1 states the peak wait
but does not give the exact pre-11:45 wait. The main post's first chunk, with
both `20 to 25 minutes` and `under 5 minutes`, ranks fifth (distance 0.450515).
Reducing top-k to 3 or 4 would lose part of that answer. Other dining halls also
appear in the five results, so the model must distinguish the named place.
The starter grounding instruction requires using only the supplied documents,
refusing unsupported claims, and naming the file used.

This is calibration on ten known questions, not a guarantee for unseen or
near-topic questions. Similar campus language can still pass the gate even
when a particular requested fact is absent. The prompt's refusal instruction
remains the second layer.

## How I Used AI

The implementation, measurements, and this write-up were prepared with Codex.
The following describes the actual requests and corrections in this session;
it does not claim that the student manually wrote the generated code.

**1. Initial request and corpus-specific changes.** The initial request was
"Complete the assignment." Codex read the starter and the campus posts,
observed that the starter kept all 88 posts whole, and implemented a paragraph
chunker. The replacement uses a 350-character soft target, repeats source
titles, and removes body overlap; its tests verify that no body paragraph is
lost or duplicated. These changes came from the separate dining/course
paragraphs and the single qualified housing-lottery explanation.

**2. Scope and acceptance criteria.** After the initial request, the Week 1
CodePath link clarified that the task was the build and criteria, rather than
both weeks of the starter template. The work was narrowed to Week 1. When asked
to finish the remaining criteria, Codex drafted a strict chunk-focus target
and a complete-answer target. The answer target was made more specific than a
single `expects` keyword: its table requires every price, time window, and
qualification requested by each question, with supporting sources. The
chunk-focus target deliberately goes beyond the existing content-preservation
tests, since an intact chunk can still mix unrelated housing topics.

The implementation and custom criteria were drafted by Codex at the user's
request. Criteria 4–5 were completed after the Week 1 observations and sample
answer; the commit history and `criteria.md` disclose that timing. No
independent student authorship or earlier chronology is claimed. After the
API credential was added locally, the sample was captured from real model
calls rather than simulated output.

No stretch feature is claimed.

---

# Week 2

Reserved for the next unit. The three-run before/after evaluation, verdicts,
diagnoses, and improvement will be added here using the existing criteria and
commit history. No Week 2 scores are claimed in this Week 1 submission.
