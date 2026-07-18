from reqquality.synthetic import SyntheticRequirementsConfig, generate_synthetic_requirements, synthetic_traceability


def test_synthetic_requirements_have_expected_columns():
    frame = generate_synthetic_requirements(SyntheticRequirementsConfig(seed=3, repeat_templates=2))
    assert len(frame) >= 20
    assert {"requirement_id", "text", "module", "requirement_type", "ground_truth_quality"}.issubset(frame.columns)
    assert frame["requirement_id"].is_unique


def test_traceability_links_match_requirements():
    frame = generate_synthetic_requirements(SyntheticRequirementsConfig(seed=3, repeat_templates=1))
    trace = synthetic_traceability(frame)
    assert len(trace) == len(frame)
    assert set(trace["requirement_id"]) == set(frame["requirement_id"])


def test_invalid_config_rejected():
    try:
        SyntheticRequirementsConfig(repeat_templates=0)
    except ValueError:
        assert True
    else:
        raise AssertionError("invalid repeat_templates should fail")
