"""Tests for the eval harness. No network, no API key."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import run  # noqa: E402
from dashboard import generate  # noqa: E402
from grading import assertions, human_review, llm_judge  # noqa: E402

DATA = ROOT / "data" / "v1"


@pytest.fixture(scope="module")
def examples():
    return {e["id"]: e for e in run.load_examples(DATA / "examples.jsonl", "v1")}


@pytest.fixture(scope="module")
def outputs():
    return {r["id"]: r["memo"] for r in run.load_jsonl(DATA / "sample_outputs.jsonl")}


@pytest.fixture(scope="module")
def dry_run(examples, outputs):
    return run.run_eval(list(examples.values()), outputs, llm_judge.stub_judge, "stub", "v1")


# ---- assertions ----

def test_surfaced_clauses_keep_memo_order():
    memo = "- Section 4 (Liability): HIGH. x\n- Section 2.1 (Fees): low. y\nSection 9 is fine."
    assert assertions.surfaced_clauses(memo) == [{"section": "4", "risk": "high"}]
    assert assertions.cited_sections(memo) == ["4", "2.1", "9"]


def test_clean_memo_passes(examples, outputs):
    r = assertions.check(examples["ex-002"], outputs["ex-002"])
    assert r["scores"] == {"C1": 1, "C3": 1.0}
    assert r["hard_fails"] == []
    assert r["facts"]["risk_accuracy"] == 1.0
    assert r["facts"]["priority_order_correct"]


def test_missed_material_clause_is_a_hard_fail(examples, outputs):
    r = assertions.check(examples["ex-003"], outputs["ex-003"])
    assert r["scores"]["C1"] == 0
    assert any("material" in f for f in r["hard_fails"])


def test_cited_section_that_does_not_exist_is_a_hard_fail(examples, outputs):
    r = assertions.check(examples["ex-004"], outputs["ex-004"])
    assert r["scores"] == {"C1": 1, "C3": 0.67}
    assert any("section 9" in f for f in r["hard_fails"])


def test_risk_accuracy_weights_material_clauses_double(examples, outputs):
    r = assertions.check(examples["ex-005"], outputs["ex-005"])
    assert r["facts"]["risk_accuracy"] == 0.67  # 4 of 6 weighted points


def test_hedging_and_priority_order_are_caught(examples, outputs):
    facts = assertions.check(examples["ex-006"], outputs["ex-006"])["facts"]
    assert facts["hedging_phrases"] == ["may be a concern"]
    assert not facts["priority_order_correct"]


def test_memo_with_no_citations_scores_zero_on_c3(examples):
    assert assertions.check(examples["ex-001"], "Looks fine.")["scores"]["C3"] == 0.0


def test_assertions_are_reproducible(examples, outputs):
    a = assertions.check(examples["ex-005"], outputs["ex-005"])
    assert a == assertions.check(examples["ex-005"], outputs["ex-005"])


# ---- eval-set contract ----

def write_jsonl(path, rows):
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def test_example_without_expected_output_is_rejected(tmp_path, examples):
    bad = dict(examples["ex-001"])
    del bad["expected"]
    write_jsonl(tmp_path / "e.jsonl", [bad])
    with pytest.raises(run.EvalSetError, match="expected"):
        run.load_examples(tmp_path / "e.jsonl", "v1")


def test_example_from_another_rubric_version_is_rejected(tmp_path, examples):
    write_jsonl(tmp_path / "e.jsonl", [examples["ex-001"]])
    with pytest.raises(run.EvalSetError, match="new eval-set version"):
        run.load_examples(tmp_path / "e.jsonl", "v2")


def test_duplicate_ids_and_bad_json_are_rejected(tmp_path, examples):
    write_jsonl(tmp_path / "e.jsonl", [examples["ex-001"], examples["ex-001"]])
    with pytest.raises(run.EvalSetError, match="Duplicate"):
        run.load_examples(tmp_path / "e.jsonl", "v1")
    (tmp_path / "bad.jsonl").write_text("{not json}\n", encoding="utf-8")
    with pytest.raises(run.EvalSetError, match="line 1"):
        run.load_jsonl(tmp_path / "bad.jsonl")


def test_missing_system_output_is_rejected(examples):
    with pytest.raises(run.EvalSetError, match="No system output"):
        run.run_eval(list(examples.values()), {}, llm_judge.stub_judge, "stub", "v1")


# ---- judge ----

GOOD = {c: {"score": 1, "reasoning": "quotes 'Section 4'", "confidence": 70} for c in llm_judge.CRITERIA}


def test_parse_grade_accepts_a_complete_grade():
    grade = llm_judge.parse_grade(json.dumps(GOOD))
    assert grade["C2"] == {"score": 1.0, "reasoning": "quotes 'Section 4'", "confidence": 70}


@pytest.mark.parametrize("raw", [
    "not json",
    json.dumps({k: v for k, v in GOOD.items() if k != "C4"}),
    json.dumps({**GOOD, "C1": {"score": 3, "reasoning": "", "confidence": 50}}),
    json.dumps({**GOOD, "C1": {"score": 1, "reasoning": "", "confidence": 500}}),
    json.dumps({**GOOD, "C1": {"reasoning": "no score"}}),
    json.dumps(["a list"]),
])
def test_parse_grade_rejects_bad_responses(raw):
    with pytest.raises(llm_judge.JudgeError):
        llm_judge.parse_grade(raw)


def test_judge_prompt_and_message_carry_the_rubric_contract_and_memo(examples):
    msg = llm_judge.build_user_message(examples["ex-002"], "MEMO TEXT", "RUBRIC TEXT", "PLAYBOOK TEXT")
    for part in ("RUBRIC TEXT", "PLAYBOOK TEXT", "MEMO TEXT", "Section 4 (Liability)"):
        assert part in msg
    assert "You are NOT grading the underlying contract" in llm_judge.JUDGE_PROMPT


class FakeBlock:
    type = "text"

    def __init__(self, text):
        self.text = text


class FakeResponse:
    def __init__(self, stop_reason, text=None):
        self.stop_reason = stop_reason
        self.content = [FakeBlock(text)] if text is not None else []


class FakeClient:
    def __init__(self, response):
        self.response, self.kwargs = response, None
        self.messages = self

    def create(self, **kwargs):
        self.kwargs = kwargs
        return self.response


def test_llm_judge_sends_the_schema_and_parses_the_reply(examples, monkeypatch):
    monkeypatch.setenv("JUDGE_MODEL", "some-model")
    client = FakeClient(FakeResponse("end_turn", json.dumps(GOOD)))
    grade = llm_judge.llm_judge(examples["ex-002"], "memo", "rubric", "playbook", client=client)
    assert grade["C1"]["score"] == 1.0
    assert client.kwargs["model"] == "some-model"
    assert client.kwargs["system"] == llm_judge.JUDGE_PROMPT
    assert client.kwargs["output_config"]["format"]["schema"] == llm_judge.SCHEMA


@pytest.mark.parametrize("response", [FakeResponse("refusal"), FakeResponse("max_tokens", "{"), FakeResponse("end_turn")])
def test_llm_judge_raises_when_the_model_gives_no_grade(examples, response):
    with pytest.raises(llm_judge.JudgeError):
        llm_judge.llm_judge(examples["ex-002"], "memo", "rubric", "playbook", client=FakeClient(response))


def test_a_judge_error_leaves_the_case_ungraded_and_the_run_not_cleared(examples, outputs):
    def broken(*_):
        raise llm_judge.JudgeError("declined")
    result = run.run_eval([examples["ex-002"]], outputs, broken, "x", "v1")
    assert result["cases"][0]["aggregate"] is None
    assert result["cases"][0]["judge_error"] == "declined"
    assert result["cases_graded"] == 0 and not result["cleared"]


# ---- aggregation and the full dry run ----

def test_aggregate_uses_the_rubric_weights():
    assert run.aggregate({"C1": 1, "C2": 1.0, "C3": 1.0, "C4": 1}) == 100.0
    assert run.aggregate({"C1": 0, "C2": 0.5, "C3": 1.0, "C4": 0}) == 30.0


def test_dry_run_scores(dry_run):
    by_id = {c["id"]: c for c in dry_run["cases"]}
    assert by_id["ex-002"]["aggregate"] == 100.0
    assert by_id["ex-003"]["aggregate"] == 60.0   # C1 missed
    assert by_id["ex-005"]["aggregate"] == 90.1
    assert by_id["ex-006"]["aggregate"] == 85.0   # C4 failed
    assert dry_run["hard_fail_cases"] == 2
    assert not dry_run["cleared"]                 # hard fails block clearance


def test_a_clean_run_clears(examples, outputs):
    result = run.run_eval([examples["ex-001"], examples["ex-002"]], outputs, llm_judge.stub_judge, "stub", "v1")
    assert result["aggregate"] == 100.0 and result["cleared"]


def test_summary_is_plain_language(dry_run):
    text = run.summary(dry_run)
    assert "NOT CLEARED" in text and "ex-003" in text and "Missed a material clause" in text


# ---- calibration ----

def test_agreement_rules():
    assert human_review.agrees("C1", 1.0, 1) and not human_review.agrees("C4", 1.0, 0)
    assert human_review.agrees("C2", 0.67, 0.7) and not human_review.agrees("C2", 0.5, 0.8)


def test_agreement_report_on_the_sample_set(dry_run):
    report = human_review.agreement(dry_run["cases"])
    assert report["C1"]["agreement"] == 1.0
    assert report["C4"]["agreement"] == 0.83      # the stub cannot read for legalese
    assert all(not r["trusted"] for r in report.values())   # 6 labels is not 50
    assert "6 of 50" in report["C1"]["status"]


def test_judge_is_trusted_only_with_enough_labels_and_agreement():
    def case(judge, human):
        return {"judge": {c: {"score": judge} for c in llm_judge.CRITERIA}, "human_labels": {c: human for c in llm_judge.CRITERIA}}
    good = human_review.agreement([case(1, 1)] * 50)
    assert all(r["trusted"] for r in good.values())
    weak = human_review.agreement([case(1, 1)] * 35 + [case(1, 0)] * 15)   # 70 percent
    assert not weak["C1"]["trusted"] and "below" in weak["C1"]["status"]
    assert human_review.agreement([])["C1"]["agreement"] is None


def test_sample_puts_hard_fails_first_and_writes_a_sheet(dry_run, tmp_path):
    picked = human_review.sample(dry_run["cases"], 3)
    assert {c["id"] for c in picked[:2]} == {"ex-003", "ex-004"} and len(picked) == 3
    human_review.write_sheet(picked, tmp_path / "sheet.csv")
    assert (tmp_path / "sheet.csv").read_text(encoding="utf-8").startswith("id,category,memo")


# ---- command line and dashboard ----

def test_cli_dry_run_writes_results_and_dashboard(tmp_path, capsys):
    assert run.main(["--dry-run", "--runs-dir", str(tmp_path)]) == 0
    written = sorted(p.suffix for p in tmp_path.iterdir())
    assert written == [".json", ".md"]
    run_file = next(tmp_path.glob("*.json"))
    assert run_file.name.endswith("-stub-judge-v1.json")
    assert human_review.main(["agreement", str(run_file)]) == 0
    assert "C4: agreement 83%" in capsys.readouterr().out

    out = tmp_path / "index.html"
    assert generate.main(["--runs-dir", str(tmp_path), "--out", str(out)]) == 0
    page = out.read_text(encoding="utf-8")
    assert "Not cleared" in page and "ex-004" in page


def test_dashboard_with_no_runs_and_escaping(tmp_path, dry_run):
    assert "No runs yet" in generate.render(generate.load_runs(tmp_path))
    nasty = json.loads(json.dumps(dry_run))
    nasty["model"] = "<script>"
    assert "<script>" not in generate.render([nasty])


def test_cli_reports_a_broken_eval_set(tmp_path, capsys):
    (tmp_path / "o.jsonl").write_text("", encoding="utf-8")
    assert run.main(["--dry-run", "--outputs", str(tmp_path / "o.jsonl"), "--runs-dir", str(tmp_path)]) == 2
    assert "No system output" in capsys.readouterr().err
