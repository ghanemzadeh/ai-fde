"""Sampling and calibration hooks for the cases that need a human.

Two jobs:

  sample     write a CSV sheet of cases for a human reviewer to grade
  agreement  compare the judge's scores in a run with the human labels in
             the eval set, criterion by criterion

The calibration contract from Appendix A.3 of the book: calibrate the judge
against fifty human-labeled examples before using it for grading, calibrate
again when the model changes, and keep the calibration data in version
control. The human labels live in examples.jsonl for that reason.

    python -m grading.human_review sample runs/<run>.json --n 5
    python -m grading.human_review agreement runs/<run>.json
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

AGREEMENT_THRESHOLD = 0.80   # below this, keep grading the criterion by hand
MIN_LABELS = 50              # the calibration contract
TOLERANCE = 0.10             # for percentage criteria (C2, C3)
BINARY = ("C1", "C4")


def agrees(criterion: str, judge: float, human: float) -> bool:
    if criterion in BINARY:
        return round(judge) == round(human)
    return abs(judge - human) <= TOLERANCE


def agreement(cases: list[dict]) -> dict:
    """Judge-versus-human agreement per criterion.

    Each case needs `judge` ({criterion: {score}}) and `human_labels`
    ({criterion: score}). Cases without a human label for a criterion are
    skipped for that criterion.
    """
    report = {}
    for c in ("C1", "C2", "C3", "C4"):
        pairs = [
            (case["judge"][c]["score"], case["human_labels"][c])
            for case in cases
            if case.get("judge") and c in (case.get("human_labels") or {})
        ]
        n = len(pairs)
        rate = round(sum(agrees(c, j, h) for j, h in pairs) / n, 2) if n else None
        trusted = bool(n >= MIN_LABELS and rate is not None and rate >= AGREEMENT_THRESHOLD)
        if n == 0:
            status = "No human labels yet. Grade this criterion by hand."
        elif n < MIN_LABELS:
            status = f"Only {n} of {MIN_LABELS} human labels. Not calibrated; keep grading by hand."
        elif not trusted:
            status = f"Agreement is below {AGREEMENT_THRESHOLD:.0%}. Fix the rubric and keep grading by hand."
        else:
            status = "Calibrated. The judge can grade this criterion."
        report[c] = {"labels": n, "agreement": rate, "trusted": trusted, "status": status}
    return report


def sample(cases: list[dict], n: int, seed: int = 0) -> list[dict]:
    """Pick cases for human review: every hard fail first, then a random sample."""
    failed = [c for c in cases if c["hard_fails"]]
    rest = [c for c in cases if not c["hard_fails"]]
    random.Random(seed).shuffle(rest)
    return (failed + rest)[: max(n, len(failed))]


def write_sheet(cases: list[dict], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "category", "memo", "hard_fails", "judge_C2", "judge_C4", "human_C1", "human_C2", "human_C3", "human_C4", "notes"])
        for c in cases:
            judge = c.get("judge") or {}
            w.writerow([
                c["id"], c["category"], c["memo"], " ".join(c["hard_fails"]),
                judge.get("C2", {}).get("score", ""), judge.get("C4", {}).get("score", ""),
                "", "", "", "", "",
            ])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample", help="write a review sheet")
    s.add_argument("run")
    s.add_argument("--n", type=int, default=5)
    s.add_argument("--out", default="review-sheet.csv")
    a = sub.add_parser("agreement", help="print judge-versus-human agreement")
    a.add_argument("run")
    args = p.parse_args(argv)

    run = json.loads(Path(args.run).read_text(encoding="utf-8"))
    if args.cmd == "sample":
        picked = sample(run["cases"], args.n)
        write_sheet(picked, Path(args.out))
        print(f"Wrote {len(picked)} cases to {args.out}")
    else:
        for c, r in agreement(run["cases"]).items():
            rate = "n/a" if r["agreement"] is None else f"{r['agreement']:.0%}"
            print(f"{c}: agreement {rate} on {r['labels']} labels. {r['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
