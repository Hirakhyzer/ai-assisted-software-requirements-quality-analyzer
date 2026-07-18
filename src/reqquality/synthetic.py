"""Deterministic synthetic software requirements corpus.

The corpus is intentionally fictional and includes good and flawed requirements
for testing ambiguity, missing acceptance criteria, conflicts, traceability,
risk, and testability analysis without exposing private specifications.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

REQUIREMENT_TYPES = ["functional", "security", "privacy", "performance", "usability", "compliance", "operational", "data"]
MODULES = ["Authentication", "Payments", "Notifications", "Analytics", "Admin Console", "Mobile App"]


@dataclass(frozen=True)
class SyntheticRequirementsConfig:
    seed: int = 42
    repeat_templates: int = 3

    def __post_init__(self) -> None:
        if self.repeat_templates < 1:
            raise ValueError("repeat_templates must be positive")


BASE_REQUIREMENTS: list[dict[str, object]] = [
    {"template_id": "AUTH-LOGIN-MFA", "module": "Authentication", "requirement_type": "security", "text": "The system shall require multi-factor authentication for administrator login using a registered second factor.", "priority": "high", "actor": "administrator", "acceptance_criteria": "Given an administrator account, when password login succeeds, then a second factor challenge is required before access is granted.", "linked_test_case": "TC-AUTH-001", "ground_truth_quality": "good"},
    {"template_id": "AUTH-FAST-LOGIN", "module": "Authentication", "requirement_type": "functional", "text": "The login process should be fast and easy for all users.", "priority": "", "actor": "user", "acceptance_criteria": "", "linked_test_case": "", "ground_truth_quality": "ambiguous"},
    {"template_id": "PAY-PCI-STORAGE", "module": "Payments", "requirement_type": "compliance", "text": "The payment service shall not store full card numbers after authorization and shall retain only tokenized payment references.", "priority": "critical", "actor": "payment service", "acceptance_criteria": "Given a completed payment, then the transaction record contains a token and does not contain a full card number.", "linked_test_case": "TC-PAY-003", "ground_truth_quality": "good"},
    {"template_id": "PAY-CARD-RETAIN-CONFLICT", "module": "Payments", "requirement_type": "data", "text": "The payment service shall store full card numbers for later customer support lookup.", "priority": "medium", "actor": "payment service", "acceptance_criteria": "Support staff can retrieve the full card number from the transaction record.", "linked_test_case": "TC-PAY-004", "ground_truth_quality": "conflict"},
    {"template_id": "NOTIFY-SOME-USERS", "module": "Notifications", "requirement_type": "functional", "text": "The platform should notify users whenever appropriate.", "priority": "medium", "actor": "platform", "acceptance_criteria": "", "linked_test_case": "", "ground_truth_quality": "ambiguous"},
    {"template_id": "ANALYTICS-DASHBOARD", "module": "Analytics", "requirement_type": "functional", "text": "Managers shall view a daily usage dashboard containing active users, failed jobs, and average response time.", "priority": "medium", "actor": "manager", "acceptance_criteria": "Given a manager opens the dashboard, then the three metrics are visible for the selected day.", "linked_test_case": "TC-ANA-002", "ground_truth_quality": "good"},
    {"template_id": "PERF-RESPONSE-TIME", "module": "Mobile App", "requirement_type": "performance", "text": "The mobile app shall load the home screen in under 2 seconds for 95% of requests on a 4G connection.", "priority": "high", "actor": "mobile app", "acceptance_criteria": "Load-test results show p95 home-screen load time below 2 seconds under the configured 4G profile.", "linked_test_case": "TC-MOB-009", "ground_truth_quality": "good"},
    {"template_id": "PERF-FAST-SYSTEM", "module": "Mobile App", "requirement_type": "performance", "text": "The system must always be extremely fast.", "priority": "high", "actor": "", "acceptance_criteria": "", "linked_test_case": "", "ground_truth_quality": "untestable"},
    {"template_id": "PRIVACY-DELETE", "module": "Admin Console", "requirement_type": "privacy", "text": "Users shall be able to request deletion of their profile data, and deletion status shall be visible to support staff.", "priority": "high", "actor": "user", "acceptance_criteria": "Given a deletion request, when the workflow completes, then profile data is marked deleted and support sees the status.", "linked_test_case": "", "ground_truth_quality": "missing_trace"},
    {"template_id": "OPS-BACKUP", "module": "Admin Console", "requirement_type": "operational", "text": "The system shall create encrypted database backups every 24 hours and keep recoverable backups for 30 days.", "priority": "high", "actor": "system", "acceptance_criteria": "Backup logs show one encrypted backup per 24-hour window and restore tests succeed for a 30-day sample.", "linked_test_case": "TC-OPS-007", "ground_truth_quality": "good"},
    {"template_id": "AUTH-PASSWORD-RESET", "module": "Authentication", "requirement_type": "security", "text": "Password reset links shall expire within 15 minutes and may be used only once.", "priority": "critical", "actor": "user", "acceptance_criteria": "Given a reset link, then it is rejected after 15 minutes or after successful first use.", "linked_test_case": "TC-AUTH-006", "ground_truth_quality": "good"},
    {"template_id": "AUTH-PASSWORD-RESET-CONFLICT", "module": "Authentication", "requirement_type": "security", "text": "Password reset links shall remain valid for 7 days so users have enough time.", "priority": "low", "actor": "user", "acceptance_criteria": "A password reset link works for 7 days after it is issued.", "linked_test_case": "TC-AUTH-007", "ground_truth_quality": "conflict"},
]


def generate_synthetic_requirements(config: SyntheticRequirementsConfig | None = None) -> pd.DataFrame:
    """Generate a deterministic requirements table."""
    cfg = config or SyntheticRequirementsConfig()
    rng = np.random.default_rng(cfg.seed)
    rows: list[dict[str, object]] = []
    rid = 1
    for repeat in range(cfg.repeat_templates):
        for template in BASE_REQUIREMENTS:
            rows.append({
                "requirement_id": f"REQ-{rid:04d}",
                "template_id": template["template_id"],
                "module": template["module"],
                "requirement_type": template["requirement_type"],
                "text": str(template["text"]) + _variation_suffix(repeat, rng),
                "priority": template["priority"],
                "actor": template["actor"],
                "acceptance_criteria": template["acceptance_criteria"],
                "linked_test_case": template["linked_test_case"],
                "source_document": f"synthetic_spec_{1 + repeat % 2}.md",
                "release": f"R{1 + repeat}",
                "ground_truth_quality": template["ground_truth_quality"],
                "data_origin": "synthetic fictional software requirement",
            })
            rid += 1
    return pd.DataFrame(rows)


def synthetic_traceability(requirements: pd.DataFrame) -> pd.DataFrame:
    """Build a traceability table from requirements to tests/design components."""
    rows = []
    for req in requirements.itertuples(index=False):
        rows.append({
            "requirement_id": req.requirement_id,
            "design_component": req.module.replace(" ", "_").lower(),
            "linked_test_case": req.linked_test_case,
            "has_design_link": True,
            "has_test_link": bool(str(req.linked_test_case).strip()),
        })
    return pd.DataFrame(rows)


def _variation_suffix(repeat: int, rng: np.random.Generator) -> str:
    if repeat == 0:
        return ""
    suffixes = [
        " This belongs to the planned release scope.",
        " This is included in the pilot deployment.",
        " This requirement is reviewed by product and QA.",
    ]
    return " " + suffixes[int(rng.integers(0, len(suffixes)))]
