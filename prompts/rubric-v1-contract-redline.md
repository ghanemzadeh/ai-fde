# Rubric v1: Vendor-Contract Redline Memo

From *Forward Deployed AI Engineering* by Nasser Ghanemzadeh — Chapter 9.

> This copy differs from the printed book in one way: the reviewer's title is replaced with a generic one. The wording is otherwise as printed.

The first rubric drafted for a contract-review system, with four criteria scored independently. The version it grew into is in [the worked example](../templates/A08-eval-rubric-worked-example.md).

```
RUBRIC v1 — vendor-contract redline memo
=========================================

C1. CLAUSE COVERAGE
   The memo identifies every clause that diverges from the
   firm's standard playbook.
   Score: 1 (all divergent clauses surfaced) / 0 (any missed)
   Hard fail: missing a clause flagged as material in the
   playbook is a hard fail regardless of other scores.

C2. RISK ACCURACY
   For each surfaced clause, the memo correctly characterizes
   the risk as high / medium / low according to the playbook.
   Score: pct correct, weighted 2x for material clauses.

C3. CITATION CORRECTNESS
   Every claim in the memo cites the section of the contract
   it refers to, and the section number matches.
   Score: pct of citations that resolve correctly.

C4. ATTORNEY USABILITY
   The memo is ordered by risk priority, uses plain language,
   and is under 600 words.
   Score: 1 / 0, judged by the customer's reviewer on a five-question
   checklist (priority order, plain language, length, no
   hedging language, no fabricated clauses).
```
