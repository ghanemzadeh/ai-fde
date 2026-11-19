# LLM-Judge Grading Prompt

From *Forward Deployed AI Engineering* by Nasser Ghanemzadeh — Chapter 9.

> Illustrative. Adapt it to your own rubric before you run it, and calibrate the judge against human labels before you trust it.

```
You are grading a contract-review memo produced by an AI
system. You are NOT grading the underlying contract. You
are grading whether the memo would be useful to a busy
in-house attorney reviewing the contract.

For each category C1–C4 in the attached rubric, output:
  - the score (per rubric)
  - one sentence of reasoning that cites a specific phrase
    from the memo or contract
  - a confidence score 0–100

DO NOT:
  - default to "looks fine" without identifying specific
    evidence
  - score above 80 confidence on any item where you cannot
    quote the supporting evidence
  - reward verbose memos; the rubric penalizes length above
    600 words
```

A runnable version that uses this prompt is in [eval-harness/](../eval-harness/).
