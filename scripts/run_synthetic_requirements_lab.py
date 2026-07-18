"""Run the complete synthetic requirements quality analysis lab.

This command uses only fictional software requirements. It demonstrates parsing,
ambiguity detection, missing-information checks, conflict detection, risk scoring,
traceability auditing, testability analysis, reporting, figures, and a hash-chained
audit trail without exposing private company specifications.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from reqquality.audit import append_record, verify_log
from reqquality.config import ensure_output_dirs, set_seed
from reqquality.conflicts import detect_conflicts, detect_duplicates
from reqquality.parsing import parse_requirement_table
from reqquality.quality_checks import run_quality_checks
from reqquality.reporting import write_report
from reqquality.scoring import module_quality_summary, score_requirements, summarize_quality
from reqquality.synthetic import SyntheticRequirementsConfig, generate_synthetic_requirements, synthetic_traceability
from reqquality.traceability import acceptance_criteria_patterns, traceability_audit
from reqquality.visualization import plot_conflict_matrix, plot_issue_counts, plot_quality_by_module, plot_quality_distribution, plot_review_priority


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a synthetic AI-assisted software requirements quality analyzer.")
    parser.add_argument("--repeat-templates", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    set_seed(args.seed)
    outputs = ensure_output_dirs(args.output_dir)
    requirements = generate_synthetic_requirements(SyntheticRequirementsConfig(seed=args.seed, repeat_templates=args.repeat_templates))
    trace_links = synthetic_traceability(requirements)
    parsed = parse_requirement_table(requirements)
    checks = run_quality_checks(parsed)
    conflicts = detect_conflicts(parsed)
    duplicates = detect_duplicates(parsed)
    trace_audit = traceability_audit(parsed, trace_links)
    acceptance_patterns = acceptance_criteria_patterns(parsed)
    scores = score_requirements(parsed, checks, conflicts, trace_audit)
    module_summary = module_quality_summary(scores)
    summary = summarize_quality(scores, conflicts, checks, trace_audit)
    summary.update({"seed": args.seed, "repeat_templates": args.repeat_templates, "duplicate_pair_count": int(len(duplicates))})

    requirements.to_csv(outputs["results"] / "synthetic_requirements.csv", index=False)
    parsed.to_csv(outputs["results"] / "synthetic_parsed_requirements.csv", index=False)
    checks.to_csv(outputs["results"] / "synthetic_quality_checks.csv", index=False)
    conflicts.to_csv(outputs["results"] / "synthetic_conflict_register.csv", index=False)
    duplicates.to_csv(outputs["results"] / "synthetic_duplicate_candidates.csv", index=False)
    trace_audit.to_csv(outputs["results"] / "synthetic_traceability_audit.csv", index=False)
    acceptance_patterns.to_csv(outputs["results"] / "synthetic_acceptance_criteria_patterns.csv", index=False)
    scores.to_csv(outputs["results"] / "synthetic_requirement_quality_scores.csv", index=False)
    module_summary.to_csv(outputs["results"] / "synthetic_module_quality_summary.csv", index=False)

    audit_path = outputs["audit"] / "requirements_quality_audit_log.jsonl"
    append_record(audit_path, {**summary, "boundary": "synthetic requirements review support only"})
    summary["audit_log"] = verify_log(audit_path)
    (outputs["results"] / "synthetic_requirements_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    write_report(outputs["reports"] / "synthetic_requirements_quality_report.md", summary, scores, checks, conflicts, trace_audit, module_summary)
    plot_quality_by_module(module_summary, outputs["figures"] / "synthetic_quality_by_module.png")
    plot_issue_counts(checks, outputs["figures"] / "synthetic_issue_counts.png")
    plot_quality_distribution(scores, outputs["figures"] / "synthetic_quality_distribution.png")
    plot_conflict_matrix(conflicts, parsed, outputs["figures"] / "synthetic_conflict_matrix.png")
    plot_review_priority(scores, outputs["figures"] / "synthetic_review_priority.png")
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
