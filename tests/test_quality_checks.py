from reqquality.conflicts import detect_conflicts
from reqquality.parsing import parse_requirement_table
from reqquality.quality_checks import run_quality_checks
from reqquality.synthetic import SyntheticRequirementsConfig, generate_synthetic_requirements


def _sample():
    return parse_requirement_table(generate_synthetic_requirements(SyntheticRequirementsConfig(seed=7, repeat_templates=1)))


def test_quality_checks_find_ambiguity_and_missing_fields():
    reqs = _sample()
    checks = run_quality_checks(reqs)
    assert (checks["ambiguous_term_count"] > 0).any()
    assert checks["missing_acceptance_criteria"].any()
    assert checks["unverifiable_statement"].any()


def test_conflict_detection_finds_known_pairs():
    reqs = _sample()
    conflicts = detect_conflicts(reqs)
    assert not conflicts.empty
    assert (conflicts["conflict_score"] >= 0.55).all()
