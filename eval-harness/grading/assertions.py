"""Unit-test-style checks for the easy cases.

These checks are deterministic: the same memo and the same example always
produce the same result. They cover the mechanical parts of the rubric:

  C1  clause coverage      every divergent clause is surfaced
  C3  citation correctness every cited section exists in the contract
  hard fails               a missed material clause, or a cited section
                           that does not exist

They also collect the mechanical facts behind C2 and C4 (risk labels, word
count, hedging, ordering). The dry-run judge uses those facts. A real judge
reads the memo instead.

The memo format these checks expect is one line per surfaced clause:

    - Section 4 (Liability): HIGH. The cap is below the playbook minimum.
"""
from __future__ import annotations

import re

CITATION = re.compile(r"\bSection\s+(\d+(?:\.\d+)*)", re.IGNORECASE)
RISK = re.compile(r"\b(HIGH|MEDIUM|LOW)\b")
RISK_ORDER = {"high": 0, "medium": 1, "low": 2}
HEDGES = ("may be a concern", "might be an issue", "could potentially", "it is possible that")
MAX_WORDS = 600


def surfaced_clauses(memo: str) -> list[dict]:
    """Clauses the memo flags, in the order it flags them: [{section, risk}]."""
    out = []
    for line in memo.splitlines():
        cite, risk = CITATION.search(line), RISK.search(line)
        if cite and risk:
            out.append({"section": cite.group(1), "risk": risk.group(1).lower()})
    return out


def cited_sections(memo: str) -> list[str]:
    """Every section number the memo cites, flagged or not."""
    return CITATION.findall(memo)


def check(example: dict, memo: str) -> dict:
    """Grade one memo against one example. Returns scores, hard fails and facts."""
    real = {s["number"] for s in example["contract"]["sections"]}
    expected = example["expected"]["divergent"]
    surfaced = surfaced_clauses(memo)
    surfaced_ids = {c["section"] for c in surfaced}
    cited = cited_sections(memo)

    missed = [e["section"] for e in expected if e["section"] not in surfaced_ids]
    missed_material = [e["section"] for e in expected if e["material"] and e["section"] not in surfaced_ids]
    phantom = sorted({c for c in cited if c not in real})

    hard_fails = []
    if missed_material:
        hard_fails.append(f"Missed a material clause: section {', '.join(missed_material)}.")
    if phantom:
        hard_fails.append(f"Cited a section that is not in the contract: section {', '.join(phantom)}.")

    c1 = 0 if missed else 1
    c3 = round(sum(1 for c in cited if c in real) / len(cited), 2) if cited else 0.0

    # Facts for C2 (risk accuracy, material clauses weighted 2x).
    by_id = {c["section"]: c["risk"] for c in surfaced}
    weight = right = 0
    for e in expected:
        if e["section"] in by_id:
            w = 2 if e["material"] else 1
            weight += w
            right += w if by_id[e["section"]] == e["risk"] else 0
    risk_accuracy = round(right / weight, 2) if weight else 1.0

    # Facts for C4 (usability). Plain language cannot be checked mechanically.
    ranks = [RISK_ORDER[c["risk"]] for c in surfaced]
    facts = {
        "word_count": len(memo.split()),
        "under_word_limit": len(memo.split()) < MAX_WORDS,
        "hedging_phrases": [h for h in HEDGES if h in memo.lower()],
        "priority_order_correct": ranks == sorted(ranks),
        "risk_accuracy": risk_accuracy,
        "missed_sections": missed,
    }
    return {"scores": {"C1": c1, "C3": c3}, "hard_fails": hard_fails, "facts": facts}
