# After-change assessment

Codex judged every actual answer against the unchanged required-facts table in `criteria.md`. All 15 generated answers were read; no keyword scorer or model judge was used. Every retrieval result exactly matches its baseline counterpart.

| Question | Run 1 | Run 2 | Run 3 | Basis for passing criteria 2 and 5 |
|---|---|---|---|---|
| Housing lottery | PASS | PASS | PASS | Random numbers for rising sophomores; accumulated credits first for juniors/seniors, random tie-breaking; cites `admin_housing_lottery.txt`. |
| Morrow laundry | PASS | PASS | PASS | $1.50 wash, $1.25 dry, coin or card; cites both supporting Morrow filenames, no other residence’s prices. |
| Kestrel wait | PASS | PASS | PASS | 20–25 minutes at 12:15–1:00, under 5 minutes before 11:45; cites `dining_kestrel_commons.txt` in all three runs. Run 3 additionally cites the follow-up, which supports the peak statement. |
| CS 210 | PASS | PASS | PASS | Midterms curved, final not; lecture rather than textbook material; cites both supporting CS 210 files. |
| Library | PASS | PASS | PASS | 2am during term and 10pm during reading week; cites `study_library_hours.txt`. |

All answers contain the complete requested facts and no unsupported or contradictory claim. No final trial errors occurred. Each trial made exactly one uncached model request, so no live retry occurred.

## Deterministic chunk judgments

| Sample | Label | Judgment |
|---|---|---|
| 1 | `admin_add_drop_deadline.txt#0` | PASS — named add/drop policy, complete factual sentences, one course-change deadline topic. |
| 2 | `course_cs_210_exams.txt#0` | PASS — names CS 210; exam structure, curving, and lab preparation are the single assessment topic explicitly allowed by the original criterion. |
| 3 | `course_phys_130.txt#1` | PASS — names PHYS 130, states the lab-practical weight and preparation observation; no neighboring chunk needed. |
| 4 | `dining_the_ridgeway_cafe_followup.txt#1` | PASS — identifies the café, states seat capacity and crowding, one seating topic. “Also” does not obscure which place the factual sentence describes. |
| 5 | `housing_morrow_house.txt#0` | FAIL — identifies Morrow House and has intact sentences, but combines room layout, price, and building maintenance, which the criterion explicitly separates. |


## Gate

All five original out-of-scope questions are refused, with exactly the same distances as before and zero model calls. The separate `week2_refusal_check.txt` also records the actual refusal strings.

## Counts

Criteria 1, 2, 3, and 5: 5/5 in each displayed run. Criterion 4: 4/5 from the one deterministic sample, displayed in all three columns. No original criterion or target changed.
