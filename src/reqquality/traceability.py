"""Traceability and acceptance-criteria analysis."""

from __future__ import annotations

import pandas as pd


def traceability_audit(requirements: pd.DataFrame, traceability: pd.DataFrame) -> pd.DataFrame:
    """Evaluate whether each requirement is linked to design and tests."""
    merged = requirements.merge(traceability, on="requirement_id", how="left", suffixes=("", "_trace"))
    merged["has_acceptance_criteria"] = merged["acceptance_criteria"].fillna("").astype(str).str.len() > 0
    merged["has_test_link"] = merged["linked_test_case_trace"].fillna(merged["linked_test_case"]).fillna("").astype(str).str.len() > 0
    merged["has_design_link"] = merged["has_design_link"].fillna(False).astype(bool)
    merged["traceability_complete"] = merged["has_acceptance_criteria"] & merged["has_test_link"] & merged["has_design_link"]
    return merged[["requirement_id", "module", "requirement_type", "has_acceptance_criteria", "has_test_link", "has_design_link", "traceability_complete"]].copy()


def acceptance_criteria_patterns(requirements: pd.DataFrame) -> pd.DataFrame:
    """Classify acceptance criteria structure."""
    rows = []
    for req in requirements.itertuples(index=False):
        acceptance = str(req.acceptance_criteria or "").lower()
        rows.append({
            "requirement_id": req.requirement_id,
            "has_given_when_then": all(word in acceptance for word in ["given", "then"]) and ("when" in acceptance or "after" in acceptance or "before" in acceptance),
            "acceptance_length": len(acceptance.split()),
            "acceptance_present": bool(acceptance.strip()),
        })
    return pd.DataFrame(rows)
