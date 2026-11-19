# Eval Rubric: Worked Example

From *Forward Deployed AI Engineering* by Nasser Ghanemzadeh — Appendix A.8; see Chapter 9.

> This copy differs from the printed book in one way: the reviewer's name and the dates are replaced with placeholders. The criteria, weights and thresholds are as printed.

The rubric a contract-review engagement shipped with. Use it as a model for how specific a rubric has to be before grading begins.

```
EVAL RUBRIC v3 — vendor-contract redline memo
==============================================

Owner: [the customer's reviewing lawyer]
Date drafted: [validation, week 1]
Sign-off: [the customer's reviewing lawyer, validation week 1]

C1. CLAUSE COVERAGE
  The memo identifies every clause that diverges from
  the firm's standard playbook (Schedule B).
  Score: 1 (all divergent clauses surfaced) / 0 (any missed)
  Weight: load-bearing.

C2. RISK ACCURACY
  For each surfaced clause, the memo correctly characterizes
  the risk as high / medium / low according to the playbook
  (Schedule B).
  Score: percent correct.
  Weighted 2x on clauses flagged as "material" in the
  playbook (currently 23 of 142 standard clauses).

C3. CITATION CORRECTNESS
  Every claim in the memo cites the section of the
  contract it refers to, and the section number resolves
  to the correct text.
  Score: percent of citations that resolve correctly.

C4. ATTORNEY USABILITY
  The memo is ordered by risk priority, uses plain
  language, and is under 600 words.
  Score: 1/0 against the five-question checklist:
    - Priority order correct?
    - No legalese except where citing contract language?
    - Under 600 words?
    - No hedging language (e.g., "may be a concern")?
    - No fabricated clauses (every claim ties to a
      specific section)?

HARD FAILS
  - Missing a clause flagged as "material" in the
    playbook is a hard fail regardless of C2–C4.
  - Fabricating a clause that does not appear in the
    contract is a hard fail.
  - Citing a section that does not exist is a hard fail.

AGGREGATION
  Aggregate score = (C1 weighted 40%) + (C2 weighted 30%) +
                    (C3 weighted 15%) + (C4 weighted 15%)
  The system clears validation when aggregate ≥ 80 and
  no hard fails occur in the validation set of 131 cases.
```

The rubric is two pages. The two pages are the spec. Everything downstream (the grading code, the LLM-judge prompt, the production traces) refers back to this document.
