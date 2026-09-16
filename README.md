# The Unofficial Guide

James Paek · `campus_life` · Units 1 and 2

Implementation assistance: Codex. Work is being recorded as it is performed.

**Unit 2 complete:** Both three-run evaluations, criterion verdicts, diagnoses,
one measured improvement, remaining limitations, and AI disclosure are below.
The later batch meets four of five criteria; chunk focus still misses. The
live batches improved from 12/15 to 15/15 delivered answers, but no live retry
was needed after the change, so causal benefit is claimed only for the
controlled outage comparison. The original criteria and Unit 1 history are
preserved. Course-portal submission is left to the student, as requested.

The Week 1 material below is the historical build record. AI assistance and
the timing of the two custom criteria are disclosed in [`criteria.md`](criteria.md).

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

## Evaluation protocol

The Week 1 targets in `criteria.md` and the ten questions in `questions.py`
remain unchanged. Each configuration gets three uncached trials for each of
the five in-corpus questions, plus one deterministic pass over all five
out-of-scope questions and the five samples from `python app.py chunks -n 5`.
A target must hold in every run. An API error counts as a failed answer, never
as an accepted response. No stretch feature is planned.

`python tools/evaluate_week2.py --label before` invokes the existing
`run_eval.py` pipeline and report writer. It also preserves every retrieved
chunk, complete generated answer, source label, distance, gate decision,
request count, configuration, and corpus/criteria hash in JSON. The wrapper
records provider exceptions explicitly and continues the scheduled trials;
it does not change prompts or model behavior. Verdicts will be assigned by
reading the original required-facts table, not by keyword matches. The same
instrumentation will be used after the one improvement.


## Run Log — Before

Configuration: Week 1 pipeline at `0b4e4e6`, 115 chunks, `CHUNK_SIZE=350`,
zero body overlap, top-k 5, cosine gate 0.65, real `all-MiniLM-L6-v2` embeddings,
and `gemini-3.5-flash-lite`. Fifteen scheduled uncached requests produced
12 answers and three HTTP 503 errors. Reported usage was 7,075 tokens
(6,460 input, 615 output); failed calls did not report token usage.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. A retrieved chunk contains the complete answer | At least 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a retrieved source | 5 of 5 | 3/5 | 4/5 | 5/5 | MISSED |
| 3. Gate stops out-of-corpus questions | At least 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Sampled chunks are self-contained and focused | 5 of 5 | 4/5 | 4/5 | 4/5 | MISSED |
| 5. Complete, supported answers without source mixing | At least 4 of 5 | 3/5 | 4/5 | 5/5 | MISSED |

Runs are the first, second, and third trial of each question, as in the starter
runner (which schedules by question). Criterion 3 and chunk inspection are
single deterministic measurements repeated across the columns, as the original
criteria permit. Every scheduled in-corpus request counts in the denominator.
For criterion 2, an error provides no cited answer and therefore counts as a
miss: among answers actually generated, citation coverage was 12/12. This
separates the delivery failure from a missing-citation generation mistake.

Raw reports: [starter run log](results/run_2026-09-16_1857_before.md),
[full answers and retrieved chunks](results/week2_before_evidence.json),
[console output](results/week2_before_console.txt), and
[chunk sample](results/week2_before_chunks.txt). Detailed judgments are in
[the assessment](results/week2_before_assessment.md). No keyword scorer was
used; the blank question-level cells in the starter report are intentional.

### Real output for the five criteria

**1 — Retrieval.** Housing-lottery trial 1, rank 1:
`admin_housing_lottery.txt#0`, distance 0.191651.
Produced by `store.py::search`, text from `chunker.py::split_documents`.

```text
On the housing lottery

The housing lottery is not random in the way most people assume. Rising sophomores get a number drawn at random, but juniors and seniors are ordered by accumulated credit hours first, and only tie-break randomly. That means a senior who took summer courses reliably beats a senior who didn't. Numbers come out the second week of March and selection runs over four evenings.
```

**2 — Source attribution.** Housing-lottery trial 1, produced by
`generate.py::answer_from_chunks` via `run_eval.py::run_once`:

```text
Rising sophomores get a number drawn at random in the housing lottery, whereas juniors and seniors are ordered by accumulated credit hours first, with random tie-breaking used only when necessary.

Source: admin_housing_lottery.txt
```

The missing cited answer in Morrow House trial 1 was a real provider error,
not a refusal or fabricated answer. `generate.py::generate` raised the following;
the evaluation wrapper preserved it and continued the scheduled trials:

```text
ServerError: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
```

**3 — Relevance gate.** Actual output of
`run_eval.py::check_out_of_scope`, using `store.py::search` and `gate.py::check`:

```text
refused  (best distance 0.825)  What is the capital of Mongolia?
  refused  (best distance 0.923)  How do I change the oil in a diesel engine?
  refused  (best distance 0.886)  Who won the 1994 World Cup?
  refused  (best distance 0.849)  What is the recommended dosage of ibuprofen for a headache?
  refused  (best distance 0.864)  How do I write a for loop in Rust?
  -> gate refused 5 of 5
```

The evidence records zero model calls for this deterministic gate pass.

**4 — Chunk quality.** Fifth sampled chunk, `housing_morrow_house.txt#0`,
produced by `chunker.py::split_documents`, printed by `app.py::cmd_chunks`:

```text
Morrow House — what it's actually like

Just finished a year in this building. Built 1954, partially renovated 2008. Rooms are singles and doubles, hall bathrooms.

The good: cheapest housing tier by about $900 a year, and the singles are real singles.

The bad: known damp problem on the ground floor; two rooms were taken offline in 2024.
```

The title and sentences are intact, but room layout, price, and maintenance
are separate topics under the original criterion. This chunk fails focus.

**5 — Complete answers.** Kestrel Commons trial 1, produced by
`generate.py::answer_from_chunks` via `run_eval.py::run_once`:

```text
The wait time at Kestrel Commons is 20 to 25 minutes between 12:15 and 1:00, and under 5 minutes before 11:45 (from dining_kestrel_commons.txt).
```

Both requested time windows are answered and attributed to the source that
contains both. Morrow House and library trial 1 failed with 503 errors, so
only three of five complete answers were delivered in run 1.

### Evidence-capture note

All 15 baseline trials, the gate pass, the official Markdown report, and the
completed JSON were saved before the wrapper's final chunk-printing step hit
an argument-signature error. That reporting-only call was corrected, and
`python app.py chunks -n 5` was executed separately against the unchanged
baseline. The original console traceback is retained. No model trial was
replaced or discarded because of this instrumentation mistake.

## Verdicts

1. **MET — Retrieval:** All five questions have a single complete supporting
   chunk in their top five in every run. Kestrel's complete source is rank 5;
   the rank-1 follow-up alone is insufficient. A generation error does not
   erase the successful retrieval recorded before it.
2. **MISSED — Cited answers delivered:** Runs delivered 3, 4, and 5 cited
   answers out of five scheduled questions, short of five in every run.
   Every answer actually returned had a valid source; the misses are absent
   answers during provider errors, not invented or omitted citations.
3. **MET — Gate:** All five unrelated questions were refused before generation,
   exceeding the four-of-five target. This is one deterministic observation.
4. **MISSED — Chunks:** Four of the five deterministic samples pass. Morrow
   House combines the three housing topics the original criterion explicitly
   says to keep separate, so intact sentences do not rescue the 5/5 target.
5. **MISSED — Complete answers:** Run 1 delivers only 3/5 complete answers;
   runs 2 and 3 reach 4/5 and 5/5. The target must hold in every run, and the
   original criterion explicitly counts provider errors as misses. All twelve
   generated answers otherwise contain every required fact, name supporting
   retrieved sources, and introduce no unsupported factual claims.

The strongest counterargument to criterion 2 is that “every answer produced”
was cited: 12/12 generated answers did name sources. That is true, and is
reported separately. The stricter end-to-end verdict uses the instruction to
check all five in-corpus answers and does not give unavailable outputs a pass.
No target or original criterion was changed to fit these observations.

## Diagnoses

**Criteria 2 and 5 — generation/service stage.** Morrow House trial 1,
CS 210 trial 2, and library trial 1 each reached generation after retrieving
all required facts and passing the 0.65 gate. The provider returned HTTP 503
`UNAVAILABLE`, explicitly reporting temporary high demand. In
`generate.py::generate`, only the 429/rate-limit condition entered the retry
loop; a 503 immediately raised. The wrapper retained each exception instead
of treating it as answer text. We cannot establish the provider's internal
cause beyond its response, but we can identify why the application delivered
no answer: it did not retry that reported transient failure.

The pattern crosses laundry, course assessment, and library hours. That,
together with complete supporting chunks and successful other trials for the
same questions, argues against loading, embedding, or retrieval as the cause
of these three misses. The common mechanism is the unhandled 503 response.

**Criterion 4 — chunking stage.** In `chunker.py::split_documents`, complete
paragraphs are packed until a 350-character soft target would be exceeded.
The first Morrow House chunk fits physical room details, a housing-price
paragraph, and a damp/maintenance paragraph below that limit. A size check
preserves text but does not detect topic boundaries. Loading retained the
facts; generation is irrelevant to this deterministic failure. Other housing
chunks and the retrieved library-hours chunk also mix practical topics, so
the sampled failure is consistent with a broader weakness of size-only
paragraph packing.

## The Improvement

**Decision recorded before implementation:** extend the existing bounded
retry path in `generate.py::generate` to the provider's explicit HTTP 503
status. The diagnosis connects three failed trials across two criteria to
that one error-handling gap. Keep the existing maximum of four attempts,
exponential delays, pacing, prompt, models, corpus, top-k, gate, and chunker.
A persistent 503 must still surface as a failed trial; authorization errors
such as 403 must still fail immediately.

This may help temporary overload clear within the existing attempt budget.
It cannot guarantee provider recovery and adds latency and request attempts.
A later batch could also improve simply because provider load changed, so
both controlled retry tests and the actual before/after experiment will be
reported. The chunking problem is deliberately left for a separate experiment:
changing it at the same time would confound this one improvement.



### Run Log — After

The same five questions were asked three times with caching disabled, using
production change `e3f7711`. All 15 trials returned complete, cited answers.
All 15 succeeded on their first attempt: the live batch did not encounter a
503 or exercise a retry. Usage was 8,808 reported tokens (8,025 input, 783
output). The increased token total includes three more delivered answers;
it is not evidence of longer answers or retry cost.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. A retrieved chunk contains the complete answer | At least 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a retrieved source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | At least 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Sampled chunks are self-contained and focused | 5 of 5 | 4/5 | 4/5 | 4/5 | MISSED |
| 5. Complete, supported answers without source mixing | At least 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Criterion 1 still meets its target because every retrieved set has a chunk
containing the whole answer. Criteria 2 and 5 now meet theirs because every
scheduled trial delivered all required facts and supporting filenames, with
no unsupported or contradictory fact. Criterion 3 still rejects all five
unrelated questions with zero model calls. Criterion 4 still misses because
the unchanged Morrow House sample contains separate housing topics.

Evidence: [starter after log](results/run_2026-09-16_1902_after.md),
[full after evidence](results/week2_after_evidence.json),
[console output](results/week2_after_console.txt),
[chunk output](results/week2_after_chunks.txt), and
[per-question assessment](results/week2_after_assessment.md).

### Real output after the change

**1 — Retrieval:** Housing-lottery trial 1, `admin_housing_lottery.txt#0`,
returned by `store.py::search` from `chunker.py::split_documents`:

```text
On the housing lottery

The housing lottery is not random in the way most people assume. Rising sophomores get a number drawn at random, but juniors and seniors are ordered by accumulated credit hours first, and only tie-break randomly. That means a senior who took summer courses reliably beats a senior who didn't. Numbers come out the second week of March and selection runs over four evenings.
```

**2 — Cited answer:** Morrow House trial 1, produced by
`generate.py::answer_from_chunks` via `run_eval.py::run_once`:

```text
In Morrow House, laundry costs $1.50 to wash and $1.25 to dry, and it accepts either coin or card.

Sources: `housing_morrow_house_laundry.txt` and `housing_morrow_house.txt`
```

**3 — Gate refusal:** A separate direct check of all five out-of-scope
questions exercised `run_eval.py::run_once`, `gate.py::check`, and the real
`gate.py::REFUSAL` return path. Actual output for the first question:

```text
Question: What is the capital of Mongolia?
Gate: best distance 0.825 is over the 0.65 cutoff — refusing
I don't have enough information about that.
```

The complete [refusal check](results/week2_refusal_check.txt) confirms all five
refusal strings and zero model calls. The original evaluator's after gate
pass also refused 5/5 with zero model calls.

**4 — Chunk quality:** The same fifth sample, `housing_morrow_house.txt#0`,
printed by `app.py::cmd_chunks` from `chunker.py::split_documents`:

```text
Morrow House — what it's actually like

Just finished a year in this building. Built 1954, partially renovated 2008. Rooms are singles and doubles, hall bathrooms.

The good: cheapest housing tier by about $900 a year, and the singles are real singles.

The bad: known damp problem on the ground floor; two rooms were taken offline in 2024.
```

**5 — Complete answer:** Kestrel trial 1, produced by
`generate.py::answer_from_chunks` via `run_eval.py::run_once`:

```text
Between 12:15 and 1:00, the wait time at Kestrel Commons is 20 to 25 minutes, and before 11:45 the wait time is under 5 minutes.

Source: dining_kestrel_commons.txt
```

### Before and after, side by side

| Criterion | Before: runs 1 / 2 / 3 | After: runs 1 / 2 / 3 | Change in verdict |
|---|---|---|---|
| 1. Complete supporting chunk | 5/5 · 5/5 · 5/5 | 5/5 · 5/5 · 5/5 | MET → MET |
| 2. Cited answers delivered | 3/5 · 4/5 · 5/5 | 5/5 · 5/5 · 5/5 | MISSED → MET |
| 3. Out-of-scope gate | 5/5 · 5/5 · 5/5 | 5/5 · 5/5 · 5/5 | MET → MET |
| 4. Self-contained, focused chunks | 4/5 · 4/5 · 4/5 | 4/5 · 4/5 · 4/5 | MISSED → MISSED |
| 5. Complete grounded answers | 3/5 · 4/5 · 5/5 | 5/5 · 5/5 · 5/5 | MISSED → MET |

**Did it help?** The later live batch delivered 15/15 complete cited answers,
up from 12/15, but because it encountered no 503 responses, that increase cannot
be attributed to retries; provider conditions may explain it. Under the same
controlled sequence of a 503 followed by a successful response, the baseline
code fails after one attempt and the improved code succeeds on the second.
The change therefore fixes the diagnosed recovery gap in a controlled test,
while its live benefit remains unmeasured under an actual post-change outage.

| Controlled input (no real API call) | Baseline `0b4e4e6` | Improved code |
|---|---|---|
| 503, then success | Exception after 1 attempt | Success after 2 attempts, 1-second requested delay |

Reproduce the controlled comparison with
`python tools/check_retry_comparison.py`; its explicitly labeled
[controlled evidence](results/week2_controlled_retry_comparison.json) is
separate from the real Gemini logs and is never counted in the acceptance
scores. The [11 passing tests](results/week2_tests.txt) also verify the four
attempt limit, immediate 403 failure, existing 429 recovery, and all original
chunk-content checks.

Corpus and criteria SHA-256 values, sampled chunks, top-k, threshold, models,
every retrieved chunk and distance, and every gate decision match between
the two live configurations. Only 503 handling in `generate.py` changed the
system's behavior. Evaluation tools and tests record and verify that change.
No chunk reindexing, question changes, or replacement of failed trials occurred.

## What's Still Broken

**Criterion 4 remains missed.** The unchanged five sampled chunks still score
4/5 because the Morrow House chunk combines room details, price, and damp
maintenance. Next I would compare a topic-aware paragraph grouping strategy
with this baseline, preserving titles and complete sentences. Even individual
paragraphs sometimes mix topics, so simply lowering a character target may
not solve it. I would also re-run retrieval: splitting too finely can move
Kestrel's necessary fifth-ranked source out of the top five.

I stopped after the one generation-reliability improvement to keep the
experiment interpretable. The original 5/5 chunk target is retained. The
underlying provider can still be unavailable beyond the four-attempt budget;
retries reduce some transient failures, but do not remove that dependency.

**Coverage limits:** Only five known in-corpus questions and five clearly
unrelated questions were tested. These results do not establish robustness to
unseen questions, near-campus questions whose requested fact is absent, or
all 115 chunks. The corpus and model were held fixed throughout.

## What I'd Do Differently

- **Criterion 2:** State two separate measurements in the next unit: cited
  answers delivered / all scheduled requests, and correctly cited answers /
  answers generated. This baseline had perfect attribution among returned
  answers but incomplete delivery, which the original wording could hide.
- **Criterion 4:** Keep the 5/5 target but preselect source documents and topics
  across corpus categories, then inspect their resulting chunks. The CLI's
  evenly spaced sample changes when the total chunk count changes; fixed
  documents make a later chunking comparison easier to interpret. That issue
  does not affect this experiment, whose chunker and samples stayed identical.
- **Criterion 3:** Include near-topic unsupported questions in the next test
  suite, not only obviously unrelated ones. Passing the current five is useful
  evidence for these questions but an easy challenge for a calibrated gate.

These are proposals for the next unit. `criteria.md` and the original
questions remain unchanged in this submission.

## How I Used AI — Unit 2

The user's request was “Complete the assignment.” Codex read the Unit 2
requirements and continued the existing Unit 1 repository. The user later
specified that no course-portal submission was needed.

**Evidence and judgment:** Codex built an observation wrapper around the
starter evaluator, ran the real Gemini calls, read the returned chunks and
answers against the original fact table, and wrote the verdicts. It retained
503 errors as failures instead of substituting sample answers or retrying the
baseline until it passed. It corrected a reporting-only chunk-print call after
all baseline evidence had already been saved; the original traceback remains
in the console log. No student-only manual testing or independent authorship
is claimed.

**Diagnosis and implementation:** Codex identified the shared 503 mechanism
across three different questions and the separate paragraph-packing problem.
It chose one change, implemented bounded 503 retries, and verified transient
recovery, persistent failure, immediate 403 failure, and existing 429 behavior
with controlled tests. It also considered the counterargument that all
actually generated baseline answers were cited; the README reports both
that fact and the stricter five-request delivery counts. The student did not
supply those diagnoses or code edits. All final prose and scoring were
prepared with AI assistance and are available for the student to review.
