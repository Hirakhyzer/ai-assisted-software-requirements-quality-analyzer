"""Markdown report generation for requirements quality analysis."""

from __future__ import annotations

from pathlib import Path
import pandas as pd


def write_report(path: str | Path, summary: dict, scores: pd.DataFrame, checks: pd.DataFrame, conflicts: pd.DataFrame, traceability: pd.DataFrame, module_summary: pd.DataFrame) -> None:
    """Write a readable quality report."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    high_priority = scores.loc[scores["review_priority"] == "high"].head(12)
    lines = [
        "# Synthetic Requirements Quality Report",
        "",
        "This report is generated from fictional software requirements for research and demonstration.",
        "",
        "## Summary",
        "",
        f"- Requirements analyzed: **{summary['requirement_count']}**",
        f"- Mean quality index: **{summary['mean_quality_index']:.3f}**",
        f"- High review priority requirements: **{summary['high_review_priority_count']}**",
        f"- Ambiguity issues: **{summary['ambiguity_issue_count']}**",
        f"- Untestable issues: **{summary['untestable_issue_count']}**",
        f"- Conflict pairs: **{summary['conflict_pair_count']}**",
        f"- Traceability gaps: **{summary['traceability_gap_count']}**",
        "",
        "## Highest-priority review items",
        "",
        high_priority[["requirement_id", "module", "requirement_type", "review_priority", "requirement_quality_index", "risk_score", "text"]].to_markdown(index=False),
        "",
        "## Module quality summary",
        "",
        module_summary.to_markdown(index=False),
        "",
        "## Conflict register",
        "",
        conflicts.head(20).to_markdown(index=False) if not conflicts.empty else "No conflict pairs detected.",
        "",
        "## Traceability gaps",
        "",
        traceability.loc[~traceability["traceability_complete"]].head(20).to_markdown(index=False),
        "",
        "## Review boundary",
        "",
        "This tool supports analysts, product owners, QA engineers, and researchers. It must not automatically approve, reject, or rewrite production requirements without human review.",
    ]
    target.write_text("\n".join(lines), encoding="utf-8")
