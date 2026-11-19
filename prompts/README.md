# Prompts

The prompt and rubric from Chapter 9 of *Forward Deployed AI Engineering*, where an eval set and its judge are built for a contract-review system.

| File | What it is |
|---|---|
| [llm-judge-grading-prompt.md](llm-judge-grading-prompt.md) | The grading prompt for an LLM judge |
| [rubric-v1-contract-redline.md](rubric-v1-contract-redline.md) | The first rubric the judge grades against, with four criteria |

The judge prompt is illustrative. Rewrite it for your own rubric, then calibrate the judge against human labels before you rely on it. Chapter 9 describes how that calibration went: fast on the mechanical criteria, slow on the ones that need taste.

[eval-harness/](../eval-harness/) runs this prompt and reports how often the judge agrees with a human reviewer.
