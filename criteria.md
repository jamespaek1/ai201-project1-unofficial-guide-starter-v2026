# Acceptance criteria — The Unofficial Guide

These five targets define the Week 2 evaluation of `campus_life`. Use the five
questions in `questions.py`, top-k 5, and the configured relevance gate. For
criteria 1, 2, and 5, the target must hold in each of three uncached runs; one
passing run does not compensate for a failing run. Criterion 3 and chunk
inspection are deterministic and need one pass per configuration.

**Authorship and timing:** Criteria 1–3 are the supplied targets, with reasons
recorded before calibration. Criteria 4–5 were drafted with Codex at the user's
request after Week 1 chunk inspection, distance calibration, and the sample
answer, but before the formal Week 2 evaluation. The history preserves that
sequence; these are not represented as five independently written, pre-result
targets.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
The five questions span housing, laundry, dining, course assessment, and library hours. Four of five demands coverage across several topics while allowing one failure from similarly worded residence posts or duplicated dining/course follow-ups.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
All source filenames survive ingestion and retrieval and are included in the model prompt, so missing citations are an avoidable generation failure. Check all five in-corpus answers; the answer itself must name a retrieved document, not merely rely on the CLI’s list of retrieved sources.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.



**Why this target:**
The five supplied out-of-scope questions concern geography, engines, sports, medicine, and Rust rather than these student-life posts. Four of five demands broad rejection without assuming semantic distance perfectly separates topics; the actual gap and cutoff will be measured in Milestone 4 and recorded in the README.

---

## 4. Every sampled chunk is self-contained and focused

All **5 of 5** chunks printed by `python app.py chunks -n 5` must identify their
subject in the text, contain at least one complete factual sentence, and focus
on one topic. None may require the preceding or following chunk to establish
which place, course, or policy its facts describe.

For this check, a topic is one practical question about a subject. Exam format,
curving, and preparation count as one assessment topic; room layout, housing
price, and building maintenance are separate topics. A chunk that combines
those separate housing topics fails the focus condition even when all of its
sentences are intact. Record the five sampled labels and a pass/fail reason
for each, so another reader can reproduce the judgment.

**Why this target:**
The corpus uses one-line titles and short factual paragraphs, so every sampled
chunk should retain enough context to stand on its own. Requiring all five to
stay focused also challenges the current paragraph-packing strategy: avoiding
cut sentences alone does not prevent a chunk from mixing prices, rooms, and
maintenance. This is an intentionally stricter quality target than merely
preserving the input text, and it is not claimed to be met already.

---

## 5. Answers cover every requested detail without mixing sources

For at least **4 of 5** test questions in **each of three uncached runs**, the
answer must include every required fact in the table below, attribute those
facts to supporting retrieved filenames, and introduce no unsupported or
contradictory factual claim. Equivalent wording and time formats are accepted.
A partial answer, an in-corpus refusal, or a provider error counts as a miss;
an `expects` keyword alone is insufficient.

| Test question | Required facts | Supporting source documents |
|---|---|---|
| Housing lottery priority | Rising sophomores receive a random number; juniors and seniors are ordered by accumulated credit hours first, with random tie-breaking. | `admin_housing_lottery.txt` |
| Morrow House laundry | Wash $1.50; dry $1.25; payment by coin or card. Prices or payment methods from another residence do not count. | `housing_morrow_house_laundry.txt`, `housing_morrow_house.txt` |
| Kestrel Commons wait | 20–25 minutes between 12:15 and 1:00; under 5 minutes before 11:45. | `dining_kestrel_commons.txt`; its follow-up supports the peak figure but not the precise early wait. |
| CS 210 assessment | Midterms are curved; the final is not; exam material comes from lectures rather than the textbook. | `course_cs_210_exams.txt`, `course_cs_210.txt` |
| Library closing | 2am during term; 10pm during reading week. | `study_library_hours.txt` |

**Why this target:**
These questions ask for qualified or paired facts: different class years,
separate prices, two time windows, or midterms versus finals. Several retrieved
posts use very similar wording but describe different residences or courses,
so an answer can sound plausible and contain the expected keyword while still
getting the comparison wrong. Four of five requires reliable detail across
multiple topics while allowing one difficult case; checking every subpart is
stricter than judging source presence alone.

---

## How to keep the evaluation comparable

For criterion 1, use the required-facts table above to decide whether at least
one of the top five retrieved chunks contains the complete answer; a keyword
match alone is not evidence. For criterion 2, inspect the generated answer,
not the CLI's list of retrieved sources. For criterion 3, use all five existing
`OUT_OF_SCOPE` questions and verify refusal occurs before generation.

Keep these target statements in the repository for Week 2. If a criterion
proves impossible to measure consistently, append a dated clarification with
a reason instead of deleting the original. Do not lower a target just because
a run misses it. The Week 1 calibration and sample calls do not stand in for
the three-run acceptance evaluation.
