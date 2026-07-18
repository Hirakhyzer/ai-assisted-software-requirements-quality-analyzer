"""Requirement quality scoring."""

from __future__ import annotations

import numpy as np
import pandas as pd


def score_requirements(requirements: pd.DataFrame, checks: pd.DataFrame, conflicts: pd.DataFrame, traceability: pd.DataFrame) -> pd.DataFrame:
    """Compute requirement-level quality scores."""
    base = requirements[["requirement_id", "module", "requirement_type", "priority", "text", "ground_truth_quality"]].copy()
    check_cols = [col for col in checks.columns if col not in {"module", "requirement_type", "priority", "ground_truth_quality"}]
    out = base.merge(checks[check_cols], on="requirement_id", how="left").merge(
        traceability[["requirement_id", "traceability_complete", "has_acceptance_criteria", "has_test_link", "has_design_link"]],
        on="requirement_id",
        how="left",
    )
    conflict_ids = set(conflicts["requirement_id_a"].tolist() + conflicts["requirement_id_b"].tolist()) if not conflicts.empty else set()
    out["has_conflict"] = out["requirement_id"].isin(conflict_ids)
    out["ambiguity_score"] = np.clip(out["ambiguous_term_count"] / 3.0 + out["unverifiable_statement"].astype(float) * 0.35, 0, 1)
    out["testability_score"] = np.clip(1.0 - 0.45 * out["missing_acceptance_criteria"].astype(float) - 0.35 * out["missing_test_case"].astype(float) - 0.35 * out["unverifiable_statement"].astype(float), 0, 1)
    out["completeness_score"] = np.clip(1.0 - 0.25 * out["missing_actor"].astype(float) - 0.25 * out["missing_priority"].astype(float) - 0.30 * out["missing_acceptance_criteria"].astype(float) - 0.20 * (~out["has_design_link"].fillna(False)).astype(float), 0, 1)
    out["conflict_risk_score"] = out["has_conflict"].astype(float)
    out["traceability_score"] = out["traceability_complete"].fillna(False).astype(float)
    out["risk_score"] = np.clip(0.35 * out["security_privacy_risk"].astype(float) + 0.35 * out["has_conflict"].astype(float) + 0.20 * (1 - out["testability_score"]) + 0.10 * (1 - out["completeness_score"]), 0, 1)
    out["requirement_quality_index"] = np.clip(0.28 * (1 - out["ambiguity_score"]) + 0.24 * out["testability_score"] + 0.22 * out["completeness_score"] + 0.16 * out["traceability_score"] + 0.10 * (1 - out["conflict_risk_score"]), 0, 1)
    out["review_priority"] = out.apply(_review_priority, axis=1)
    return out.sort_values(["requirement_quality_index", "risk_score"], ascending=[True, False]).reset_index(drop=True)


def summarize_quality(scores: pd.DataFrame, conflicts: pd.DataFrame, checks: pd.DataFrame, traceability: pd.DataFrame) -> dict[str, float | int | str]:
    """Compact summary for reports and JSON."""
    return {
        "requirement_count": int(len(scores)),
        "mean_quality_index": float(scores["requirement_quality_index"].mean()) if len(scores) else 0.0,
        "high_review_priority_count": int((scores["review_priority"] == "high").sum()),
        "ambiguity_issue_count": int((checks["ambiguous_term_count"] > 0).sum()) if len(checks) else 0,
        "untestable_issue_count": int(checks["unverifiable_statement"].sum()) if len(checks) else 0,
        "conflict_pair_count": int(len(conflicts)),
        "traceability_gap_count": int((~traceability["traceability_complete"]).sum()) if len(traceability) else 0,
        "mean_testability_score": float(scores["testability_score"].mean()) if len(scores) else 0.0,
        "mean_completeness_score": float(scores["completeness_score"].mean()) if len(scores) else 0.0,
        "data_origin": "synthetic fictional software requirements",
        "decision_boundary": "research review support only; not an automatic acceptance or rejection decision",
    }


def module_quality_summary(scores: pd.DataFrame) -> pd.DataFrame:
    """Aggregate quality metrics by module."""
    return scores.groupby("module").agg(
        requirement_count=("requirement_id", "count"),
        mean_quality_index=("requirement_quality_index", "mean"),
        mean_risk_score=("risk_score", "mean"),
        high_review_priority_count=("review_priority", lambda s: int((s == "high").sum())),
        mean_testability_score=("testability_score", "mean"),
    ).reset_index().sort_values("mean_quality_index")


def _review_priority(row) -> str:
    if row.requirement_quality_index < 0.45 or row.risk_score >= 0.65 or row.has_conflict:
        return "high"
    if row.requirement_quality_index < 0.70 or row.risk_score >= 0.35:
        return "medium"
    return "low"
