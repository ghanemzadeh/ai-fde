"""Run the eval set and write the results.

    python run.py --dry-run                 # no API key needed
    python run.py                           # grades with the model judge
    python run.py --outputs my_outputs.jsonl

Each run writes two files to runs/:

    YYYY-MM-DD-<model>-<promptver>.json    per-case results
    YYYY-MM-DD-<model>-<promptver>.md      a summary a non-engineer can read
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from grading import assertions, human_review, llm_judge

HERE = Path(__file__).parent
WEIGHTS = {"C1": 40, "C2": 30, "C3": 15, "C4": 15}   # from the rubric's aggregation rule
PASS_MARK = 80
REQUIRED = ("id", "category", "contract", "expected", "rubric_version")


class EvalSetError(Exception):
    """The eval set breaks the minimum eval-set contract."""


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise EvalSetError(f"{path}, line {n}: not valid JSON ({exc.msg}).") from exc
    return rows


def load_examples(path: Path, rubric_version: str) -> list[dict]:
    """Load examples and enforce the eval-set contract.

    Every example has a labeled expected output and a labeled rubric
    category, and belongs to the rubric version in use.
    """
    examples = load_jsonl(path)
    if not examples:
        raise EvalSetError(f"{path} has no examples.")
    seen = set()
    for ex in examples:
        missing = [k for k in REQUIRED if k not in ex]
        if missing:
            raise EvalSetError(f"Example {ex.get('id', '?')} is missing: {', '.join(missing)}.")
        if ex["id"] in seen:
            raise EvalSetError(f"Duplicate example id: {ex['id']}.")
        seen.add(ex["id"])
        if not ex["category"]:
            raise EvalSetError(f"Example {ex['id']} has no rubric category.")
        if "divergent" not in ex["expected"]:
            raise EvalSetError(f"Example {ex['id']} has no labeled expected output.")
        if ex["rubric_version"] != rubric_version:
            raise EvalSetError(
                f"Example {ex['id']} was labeled against rubric {ex['rubric_version']}, not {rubric_version}. "
                "A rubric change needs a new eval-set version."
            )
    return examples


def aggregate(scores: dict) -> float:
    return round(sum(WEIGHTS[c] * scores[c] for c in WEIGHTS), 1)


def grade_case(example: dict, memo: str, judge) -> dict:
    checked = assertions.check(example, memo)
    try:
        judged, judge_error = judge(example, memo, checked), None
    except llm_judge.JudgeError as exc:
        judged, judge_error = None, str(exc)
    # The mechanical checks decide C1 and C3. The judge decides C2 and C4.
    scores = dict(checked["scores"])
    if judged:
        scores["C2"], scores["C4"] = judged["C2"]["score"], judged["C4"]["score"]
    return {
        "id": example["id"],
        "category": example["category"],
        "memo": memo,
        "scores": scores,
        "aggregate": aggregate(scores) if judged else None,
        "hard_fails": checked["hard_fails"],
        "facts": checked["facts"],
        "judge": judged,
        "judge_error": judge_error,
        "human_labels": example.get("human_labels"),
    }


def run_eval(examples: list[dict], outputs: dict, judge, model: str, version: str) -> dict:
    missing = [ex["id"] for ex in examples if ex["id"] not in outputs]
    if missing:
        raise EvalSetError(f"No system output for: {', '.join(missing)}.")
    cases = [grade_case(ex, outputs[ex["id"]], judge) for ex in examples]
    graded = [c for c in cases if c["aggregate"] is not None]
    score = round(sum(c["aggregate"] for c in graded) / len(graded), 1) if graded else None
    hard_fails = sum(1 for c in cases if c["hard_fails"])
    return {
        "date": dt.date.today().isoformat(),
        "model": model,
        "prompt_version": llm_judge.PROMPT_VERSION,
        "eval_set_version": version,
        "cases_total": len(cases),
        "cases_graded": len(graded),
        "aggregate": score,
        "hard_fail_cases": hard_fails,
        "cleared": bool(score is not None and score >= PASS_MARK and hard_fails == 0 and len(graded) == len(cases)),
        "calibration": human_review.agreement(cases),
        "cases": cases,
    }


def summary(run: dict) -> str:
    """The written artifact a non-engineer can read."""
    verdict = "CLEARED" if run["cleared"] else "NOT CLEARED"
    lines = [
        f"# Eval run, {run['date']}",
        "",
        f"**Result: {verdict}.** The system scored {run['aggregate']} out of 100 on {run['cases_graded']} "
        f"of {run['cases_total']} cases. It needs {PASS_MARK} or more and no hard fails to clear.",
        "",
        f"- Judge: {run['model']} (prompt {run['prompt_version']})",
        f"- Eval set: {run['eval_set_version']}",
        f"- Cases with a hard fail: {run['hard_fail_cases']}",
        "",
        "## Can the judge be trusted yet?",
        "",
    ]
    for c, r in run["calibration"].items():
        rate = "n/a" if r["agreement"] is None else f"{r['agreement']:.0%}"
        lines.append(f"- {c}: agrees with the human reviewer on {rate} of {r['labels']} labeled cases. {r['status']}")
    lines += ["", "## Case by case", ""]
    for case in run["cases"]:
        mark = "hard fail" if case["hard_fails"] else "ok"
        score = "not graded" if case["aggregate"] is None else f"{case['aggregate']}/100"
        lines.append(f"- **{case['id']}** ({case['category']}): {score}, {mark}. " + " ".join(case["hard_fails"]))
        if case["judge_error"]:
            lines.append(f"  - Judge error: {case['judge_error']}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Run the eval set and write the results.")
    p.add_argument("--version", default="v1", help="eval-set version folder under data/")
    p.add_argument("--outputs", help="JSONL of system outputs: {id, memo}. Defaults to the sample outputs.")
    p.add_argument("--dry-run", action="store_true", help="use the stub judge; no API key needed")
    p.add_argument("--runs-dir", default=str(HERE / "runs"))
    args = p.parse_args(argv)

    data = HERE / "data" / args.version
    try:
        examples = load_examples(data / "examples.jsonl", args.version)
        outputs = {r["id"]: r["memo"] for r in load_jsonl(Path(args.outputs) if args.outputs else data / "sample_outputs.jsonl")}
        if args.dry_run:
            model, judge = "stub", llm_judge.stub_judge
        else:
            model = llm_judge.model_name()
            rubric, playbook = llm_judge.load_text(data / "rubric.md"), llm_judge.load_text(data / "playbook.md")
            judge = lambda ex, memo, _checked: llm_judge.llm_judge(ex, memo, rubric, playbook)  # noqa: E731
        run = run_eval(examples, outputs, judge, model, args.version)
    except EvalSetError as exc:
        print(f"Eval set error: {exc}", file=sys.stderr)
        return 2

    runs_dir = Path(args.runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{run['date']}-{model}-{run['prompt_version']}"
    (runs_dir / f"{stem}.json").write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (runs_dir / f"{stem}.md").write_text(summary(run), encoding="utf-8")
    print(summary(run))
    print(f"Wrote {runs_dir / stem}.json and .md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
