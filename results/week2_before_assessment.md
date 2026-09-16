# Baseline assessment

Judged by Codex from the original `criteria.md`, full JSON retrieval, and actual answer text. No model judge or keyword-only scorer.

## Retrieval and answer judgments

All three retrieval result lists for each question were compared and are identical. One chunk contains every required fact for each question.

| Question | Complete supporting chunk | Required details found | Run 1 citations/details | Run 2 citations/details | Run 3 citations/details |
|---|---|---|---|---|---|
| Housing lottery | `admin_housing_lottery.txt#0 (rank 1)` | Random number for rising sophomores; credit hours first for juniors/seniors, with random ties. | PASS / PASS — all required facts, supporting filename, no unsupported claim | PASS / PASS — all required facts, supporting filename, no unsupported claim | PASS / PASS — all required facts, supporting filename, no unsupported claim |
| Morrow laundry | `housing_morrow_house_laundry.txt#0 (rank 1)` | Wash $1.50, dry $1.25, coin or card. The main residence chunk at rank 2 also contains all three. | MISS / MISS — 503; no answer | PASS / PASS — all required facts, supporting filename, no unsupported claim | PASS / PASS — all required facts, supporting filename, no unsupported claim |
| Kestrel wait | `dining_kestrel_commons.txt#0 (rank 5)` | 20–25 minutes 12:15–1:00, under 5 minutes before 11:45. The rank-1 follow-up alone does not establish the early wait. | PASS / PASS — all required facts, supporting filename, no unsupported claim | PASS / PASS — all required facts, supporting filename, no unsupported claim | PASS / PASS — all required facts, supporting filename, no unsupported claim |
| CS 210 | `course_cs_210_exams.txt#0 (rank 1)` | Midterms curved, final not curved, exams drawn from lectures rather than textbook. | PASS / PASS — all required facts, supporting filename, no unsupported claim | MISS / MISS — 503; no answer | PASS / PASS — all required facts, supporting filename, no unsupported claim |
| Library | `study_library_hours.txt#0 (rank 1)` | 2am during term, 10pm during reading week. | MISS / MISS — 503; no answer | PASS / PASS — all required facts, supporting filename, no unsupported claim | PASS / PASS — all required facts, supporting filename, no unsupported claim |

A provider error is not a generated answer. For criterion 2 the table counts cited answers delivered out of the five scheduled questions; all 12 returned answers cite supporting retrieved filenames. Criterion 5 explicitly requires provider errors to count as misses.

## Deterministic chunk judgments

| Sample | Label | Judgment |
|---|---|---|
| 1 | `admin_add_drop_deadline.txt#0` | PASS — named add/drop policy, complete factual sentences, one course-change deadline topic. |
| 2 | `course_cs_210_exams.txt#0` | PASS — names CS 210; exam structure, curving, and lab preparation are the single assessment topic explicitly allowed by the original criterion. |
| 3 | `course_phys_130.txt#1` | PASS — names PHYS 130, states the lab-practical weight and preparation observation; no neighboring chunk needed. |
| 4 | `dining_the_ridgeway_cafe_followup.txt#1` | PASS — identifies the café, states seat capacity and crowding, one seating topic. “Also” does not obscure which place the factual sentence describes. |
| 5 | `housing_morrow_house.txt#0` | FAIL — identifies Morrow House and has intact sentences, but combines room layout, price, and building maintenance, which the criterion explicitly separates. |

## Gate

All five original out-of-scope questions are refused; best distances are 0.824593–0.923117, above 0.65. The gate pass caused zero model requests.
