"""Model-graded checks.

The judge grades the criteria that need reading rather than counting. Its
prompt is the one printed in Chapter 9 of the book, with the rubric, the
contract and the memo attached.

Do not trust the judge until it is calibrated. Run
`python -m grading.human_review agreement` to compare it with human labels.

Set JUDGE_MODEL to change the model. Any change of model means the judge
must be calibrated again.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_MODEL = "claude-opus-5-5"
PROMPT_VERSION = "judge-v1"
CRITERIA = ("C1", "C2", "C3", "C4")

JUDGE_PROMPT = """\
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
"""

OUTPUT_NOTE = """\
Give every score as a number between 0 and 1: 1 or 0 for C1 and C4, and a
fraction for C2 and C3 (0.75 means 75 percent correct)."""

_CRITERION = {
    "type": "object",
    "properties": {
        "score": {"type": "number"},
        "reasoning": {"type": "string"},
        "confidence": {"type": "integer"},
    },
    "required": ["score", "reasoning", "confidence"],
    "additionalProperties": False,
}
SCHEMA = {
    "type": "object",
    "properties": {c: _CRITERION for c in CRITERIA},
    "required": list(CRITERIA),
    "additionalProperties": False,
}


class JudgeError(Exception):
    """The judge did not return a usable grade."""


def model_name() -> str:
    return os.environ.get("JUDGE_MODEL", DEFAULT_MODEL)


def build_user_message(example: dict, memo: str, rubric: str, playbook: str) -> str:
    contract = example["contract"]
    sections = "\n".join(f"Section {s['number']} ({s['heading']}): {s['text']}" for s in contract["sections"])
    return (
        f"<rubric>\n{rubric}\n</rubric>\n\n"
        f"<playbook>\n{playbook}\n</playbook>\n\n"
        f"<contract title=\"{contract['title']}\">\n{sections}\n</contract>\n\n"
        f"<memo>\n{memo}\n</memo>\n\n{OUTPUT_NOTE}"
    )


def parse_grade(raw: str | dict) -> dict:
    """Validate a judge response. Raises JudgeError if it is not a complete grade."""
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError as exc:
        raise JudgeError(f"Judge response is not JSON: {exc}") from exc
    grade = {}
    for c in CRITERIA:
        item = data.get(c) if isinstance(data, dict) else None
        if not isinstance(item, dict):
            raise JudgeError(f"Judge response has no grade for {c}.")
        try:
            score, confidence = float(item["score"]), int(item["confidence"])
        except (KeyError, TypeError, ValueError) as exc:
            raise JudgeError(f"Judge grade for {c} is malformed.") from exc
        if not 0 <= score <= 1 or not 0 <= confidence <= 100:
            raise JudgeError(f"Judge grade for {c} is out of range.")
        grade[c] = {"score": round(score, 2), "reasoning": str(item.get("reasoning", "")), "confidence": confidence}
    return grade


def stub_judge(example: dict, memo: str, assertion_result: dict) -> dict:
    """A stand-in judge for dry runs and tests. It needs no API key.

    It turns the mechanical facts from assertions.py into scores. It cannot
    read for plain language, so it will disagree with a human on some cases.
    That disagreement is what calibration is meant to find.
    """
    facts, scores = assertion_result["facts"], assertion_result["scores"]
    usable = facts["under_word_limit"] and not facts["hedging_phrases"] and facts["priority_order_correct"]
    note = "Dry-run stub: derived from mechanical checks, not from reading the memo."
    return {
        "C1": {"score": float(scores["C1"]), "reasoning": note, "confidence": 50},
        "C2": {"score": facts["risk_accuracy"], "reasoning": note, "confidence": 50},
        "C3": {"score": scores["C3"], "reasoning": note, "confidence": 50},
        "C4": {"score": 1.0 if usable else 0.0, "reasoning": note, "confidence": 50},
    }


def llm_judge(example: dict, memo: str, rubric: str, playbook: str, client=None) -> dict:
    """Grade one memo with a model. Needs the `anthropic` package and credentials."""
    if client is None:
        import anthropic

        client = anthropic.Anthropic()
    response = client.messages.create(
        model=model_name(),
        max_tokens=16000,
        system=JUDGE_PROMPT,
        messages=[{"role": "user", "content": build_user_message(example, memo, rubric, playbook)}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    )
    if response.stop_reason == "refusal":
        raise JudgeError("The model declined to grade this case.")
    if response.stop_reason == "max_tokens":
        raise JudgeError("The judge response was cut off before it finished.")
    text = next((b.text for b in response.content if b.type == "text"), None)
    if text is None:
        raise JudgeError("The judge returned no text.")
    return parse_grade(text)


def load_text(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")
