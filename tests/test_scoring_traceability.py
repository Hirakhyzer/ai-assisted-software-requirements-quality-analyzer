from reqquality.conflicts import detect_conflicts
from reqquality.parsing import parse_requirement_table
from reqquality.quality_checks import run_quality_checks
from reqquality.scoring import score_requirements, summarize_quality
from reqquality.synthetic import SyntheticRequirementsConfig, generate_synthetic_requirements, synthetic_traceability
from reqquality.traceability import traceability_audit


def test_scoring_outputs_quality_index_and_summary():
    reqs = parse_requirement_table(generate_synthetic_requirements(SyntheticRequirementsConfig(seed=5, repeat_templates=1)))
    checks = run_quality_checks(reqs)
    conflicts = detect_conflicts(reqs)
    trace = traceability_audit(reqs, synthetic_traceability(reqs))
    scores = score_requirements(reqs, checks, conflicts, trace)
    summary = summarize_quality(scores, conflicts, checks, trace)
    assert "requirement_quality_index" in scores.columns
    assert scores["requirement_quality_index"].between(0, 1).all()
    assert summary["requirement_count"] == len(reqs)
    assert summary["traceability_gap_count"] > 0
