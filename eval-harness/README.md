# Eval harness

A small, runnable version of the eval harness skeleton in Appendix A.3 of *Forward Deployed AI Engineering*. It grades the output of a contract-review system against a rubric, and tells you whether the model doing the grading can be trusted yet.

It is about 600 lines of Python with one runtime dependency, so you can read all of it before you adapt it.

> The sample data is invented. The contracts, the playbook and the memos were written for this repository and describe no real company. Replace them with your customer's data.

## Run it

Python 3.10 or later.

```bash
cd eval-harness
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python run.py --dry-run          # no API key needed
python dashboard/generate.py     # writes dashboard/index.html
python -m pytest                 # 36 tests, no network
```

`--dry-run` uses a stand-in judge built from mechanical checks. To grade with a model, set `ANTHROPIC_API_KEY` and run `python run.py`. That makes one model call per example, six for the sample set. Set `JUDGE_MODEL` to use a different model.

The dry run prints this:

```
**Result: NOT CLEARED.** The system scored 88.4 out of 100 on 6 of 6 cases.
It needs 80 or more and no hard fails to clear.

- C4: agrees with the human reviewer on 83% of 6 labeled cases.
  Only 6 of 50 human labels. Not calibrated; keep grading by hand.

- ex-003 (vendor-services): 60.0/100, hard fail. Missed a material clause: section 1.
- ex-004 (vendor-services): 95.0/100, hard fail. Cited a section that is not in the contract: section 9.
```

The score is above the pass mark and the run still fails, because two cases have hard fails. That is the behavior the rubric asks for.

## Layout

The layout follows the one printed in the book.

```
eval-harness/
  data/v1/
    examples.jsonl         input, expected output, category and human labels, one per line
    sample_outputs.jsonl   the memos being graded; replace with your system's output
    rubric.md              the rubric in plain language, for human labelers
    playbook.md            the standard positions the contracts are checked against
  grading/
    assertions.py          deterministic checks for the easy cases
    llm_judge.py           model-graded checks, using the Chapter 9 judge prompt
    human_review.py        review sheets and judge-versus-human agreement
  runs/                    per-run results: YYYY-MM-DD-<model>-<promptver>.json and .md
  dashboard/generate.py    turns run results into one static HTML page
  run.py                   runs the set and writes the results
  tests/
```

## What it enforces

The book sets a minimum contract for an eval set and another for an LLM judge. This is how the harness holds to each.

| The book says | The harness does |
|---|---|
| Every example has a labeled expected output and a labeled rubric category | `run.py` refuses to run if an example lacks either |
| The grading code is reproducible | `assertions.py` is deterministic and decides C1, C3 and the hard fails. Model grades can vary between runs, so each run stores every grade it used |
| Every grading run produces a written artifact a non-engineer can read | Each run writes a plain-language `.md` summary beside the `.json`, and the dashboard is one HTML page |
| The rubric is versioned, and a change needs a new eval-set version | Each example records its rubric version. `run.py` refuses examples labeled against another version |
| Calibrate the judge against fifty human-labeled examples | `human_review.py` reports agreement per criterion and marks the judge as not calibrated below fifty labels or below 80 percent agreement |
| Re-calibrate when the model changes | The model name is in every run file and file name. The harness cannot force this one; you have to do it |
| Keep the calibration data in version control | Human labels live in `examples.jsonl` |

One part of the contract is yours alone: every example should be real customer data, with appropriate handling for personal information. The sample set here is invented so that it can be public.

## Grade your own system

1. Replace `data/v1/playbook.md` and `data/v1/rubric.md` with your customer's.
2. Put real cases in `data/v1/examples.jsonl`. Have the customer's expert label the expected output and, for as many as they can, the `human_labels`.
3. Run your system on each case and write the outputs to a JSONL file of `{"id": ..., "memo": ...}`.
4. Run `python run.py --outputs your_outputs.jsonl`.
5. Run `python -m grading.human_review agreement runs/<run>.json`. Until a criterion is calibrated, grade it by hand. `python -m grading.human_review sample runs/<run>.json` writes a sheet for the reviewer.

The checks in `assertions.py` assume the memo format shown at the top of that file. If your system's output looks different, change the two regular expressions there first.

## Limits

- The mechanical citation check confirms that a cited section exists. It does not confirm that the section says what the memo claims. The judge and the human reviewer cover that.
- The dry-run judge cannot read for plain language, so it disagrees with the human label on one sample case. That is deliberate: it shows what a calibration gap looks like.
- Six examples are enough to show the mechanics and far too few to trust a score.

The code is under the [MIT License](../LICENSE).
