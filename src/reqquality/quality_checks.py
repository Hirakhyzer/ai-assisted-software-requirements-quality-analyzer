"""Rule-based quality checks for software requirements."""

from __future__ import annotations

import re
import pandas as pd
from reqquality.parsing import normalize_requirement_text

AMBIGUOUS_TERMS = ["fast", "easy", "appropriate", "user-friendly", "as needed", "usually", "efficient", "robust", "seamless", "always", "extremely", "reasonable", "etc", "some", "various", "quickly"]
RISK_TERMS = {
    "security": ["password", "authentication", "authorization", "admin", "token", "card", "encrypted"],
    "privacy": ["profile data", "deletion", "personal", "retention", "support staff"],
    "compliance": ["card", "retain", "store full", "audit", "legal"],
}


def run_quality_checks(requirements: pd.DataFrame) -> pd.DataFrame:
    """Run ambiguity, completeness, risk, and testability checks."""
    rows: list[dict[str, object]] = []
    for req in requirements.itertuples(index=False):
        text = normalize_requirement_text(req.text)
        acceptance = str(getattr(req, "acceptance_criteria", "") or "").strip()
        priority = str(getattr(req, "priority", "") or "").strip()
        actor = str(getattr(req, "actor", "") or "").strip()
        linked_test = str(getattr(req, "linked_test_case", "") or "").strip()
        ambiguous_hits = [term for term in AMBIGUOUS_TERMS if re.search(rf"\b{re.escape(term)}\b", text)]
        measurable = _has_measurable_condition(text, acceptance)
        missing_acceptance = not acceptance
        missing_priority = not priority
        missing_actor = not actor
        missing_test = not linked_test
        unverifiable = (not measurable) or any(term in text for term in ["appropriate", "easy", "extremely fast", "user-friendly"])
        risk_flags = _risk_flags(text, str(req.requirement_type))
        rows.append({
            "requirement_id": req.requirement_id,
            "module": req.module,
            "requirement_type": req.requirement_type,
            "priority": priority or "missing",
            "ambiguous_terms": ", ".join(ambiguous_hits),
            "ambiguous_term_count": len(ambiguous_hits),
            "missing_acceptance_criteria": missing_acceptance,
            "missing_priority": missing_priority,
            "missing_actor": missing_actor,
            "missing_test_case": missing_test,
            "unverifiable_statement": bool(unverifiable),
            "measurable_condition_present": bool(measurable),
            "security_privacy_risk": bool(risk_flags),
            "risk_flags": ", ".join(risk_flags),
            "ground_truth_quality": getattr(req, "ground_truth_quality", "unknown"),
        })
    return pd.DataFrame(rows)


def _has_measurable_condition(text: str, acceptance: str) -> bool:
    combined = f"{text} {acceptance.lower()}"
    numeric = bool(re.search(r"\b\d+(\.\d+)?\b", combined))
    acceptance_words = any(word in combined for word in ["given", "when", "then", "under", "p95", "before", "after", "reject"])
    observable_verbs = any(word in combined for word in ["visible", "rejected", "required", "contains", "load-test", "logs show", "succeed"])
    return numeric or (bool(acceptance.strip()) and (acceptance_words or observable_verbs))


def _risk_flags(text: str, requirement_type: str) -> list[str]:
    flags = []
    for category, terms in RISK_TERMS.items():
        if category == requirement_type or any(term in text for term in terms):
            matched = [term for term in terms if term in text]
            if matched:
                flags.append(category)
    if "store full card" in text or "full card numbers" in text:
        flags.append("sensitive_data_storage")
    return sorted(set(flags))
