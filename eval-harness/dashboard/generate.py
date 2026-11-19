"""Turn run results into a customer-facing dashboard.

    python dashboard/generate.py

Reads every runs/*.json and writes dashboard/index.html: one static page,
no JavaScript, safe to email or open from disk.
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

HERE = Path(__file__).parent

STYLE = """
body{font:16px/1.5 system-ui,sans-serif;max-width:60rem;margin:2rem auto;padding:0 1rem;color:#1c1c1c;background:#fff}
table{border-collapse:collapse;width:100%;margin:1rem 0}
th,td{border-bottom:1px solid #ddd;padding:.45rem .6rem;text-align:left;vertical-align:top}
.ok{color:#17663a}.bad{color:#a12222}.muted{color:#666}
"""


def load_runs(runs_dir: Path) -> list[dict]:
    runs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(runs_dir).glob("*.json"))]
    return sorted(runs, key=lambda r: r["date"])


def render(runs: list[dict]) -> str:
    e = html.escape
    out = ["<!doctype html><html lang='en'><head><meta charset='utf-8'>",
           "<meta name='viewport' content='width=device-width,initial-scale=1'>",
           f"<title>Eval dashboard</title><style>{STYLE}</style></head><body>",
           "<h1>Eval dashboard</h1>"]
    if not runs:
        out.append("<p>No runs yet. Run <code>python run.py --dry-run</code> first.</p></body></html>")
        return "\n".join(out)

    latest = runs[-1]
    cls, word = ("ok", "Cleared") if latest["cleared"] else ("bad", "Not cleared")
    out.append(f"<p>Latest run: <strong class='{cls}'>{word}</strong>, {e(str(latest['aggregate']))} out of 100 "
               f"on {latest['cases_graded']} of {latest['cases_total']} cases, "
               f"{latest['hard_fail_cases']} with a hard fail.</p>")

    out.append("<h2>Runs</h2><table><tr><th>Date</th><th>Judge</th><th>Eval set</th><th>Score</th><th>Hard fails</th><th>Result</th></tr>")
    for r in reversed(runs):
        cls, word = ("ok", "Cleared") if r["cleared"] else ("bad", "Not cleared")
        out.append(f"<tr><td>{e(r['date'])}</td><td>{e(r['model'])} ({e(r['prompt_version'])})</td>"
                   f"<td>{e(r['eval_set_version'])}</td><td>{e(str(r['aggregate']))}</td>"
                   f"<td>{r['hard_fail_cases']}</td><td class='{cls}'>{word}</td></tr>")
    out.append("</table>")

    out.append("<h2>Judge calibration, latest run</h2><table><tr><th>Criterion</th><th>Agreement with human</th><th>Labels</th><th>Status</th></tr>")
    for c, r in latest["calibration"].items():
        rate = "n/a" if r["agreement"] is None else f"{r['agreement']:.0%}"
        out.append(f"<tr><td>{e(c)}</td><td>{rate}</td><td>{r['labels']}</td><td>{e(r['status'])}</td></tr>")
    out.append("</table>")

    out.append("<h2>Cases, latest run</h2><table><tr><th>Case</th><th>Category</th><th>Score</th><th>C1</th><th>C2</th><th>C3</th><th>C4</th><th>Hard fails</th></tr>")
    for c in latest["cases"]:
        s = c["scores"]
        score = "not graded" if c["aggregate"] is None else str(c["aggregate"])
        fails = e(" ".join(c["hard_fails"])) or "<span class='muted'>none</span>"
        cells = "".join(f"<td>{e(str(s.get(k, '')))}</td>" for k in ("C1", "C2", "C3", "C4"))
        out.append(f"<tr><td>{e(c['id'])}</td><td>{e(c['category'])}</td><td>{e(score)}</td>{cells}<td>{fails}</td></tr>")
    out.append("</table></body></html>")
    return "\n".join(out)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Build the eval dashboard.")
    p.add_argument("--runs-dir", default=str(HERE.parent / "runs"))
    p.add_argument("--out", default=str(HERE / "index.html"))
    args = p.parse_args(argv)
    runs = load_runs(Path(args.runs_dir))
    Path(args.out).write_text(render(runs), encoding="utf-8")
    print(f"Wrote {args.out} from {len(runs)} run(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
