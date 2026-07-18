"""Conflict, duplicate, and inconsistency detection."""

from __future__ import annotations

import itertools
import pandas as pd
from reqquality.parsing import normalize_requirement_text, tokenize_requirement

CONFLICT_PATTERNS = [
    ("store full card numbers", "not store full card numbers"),
    ("valid for 7 days", "expire within 15 minutes"),
    ("retain", "delete"),
    ("shall not", "shall"),
]


def detect_conflicts(requirements: pd.DataFrame) -> pd.DataFrame:
    """Find likely contradictions between requirements in the same module/domain."""
    rows: list[dict[str, object]] = []
    for left, right in itertools.combinations(requirements.itertuples(index=False), 2):
        same_module = left.module == right.module
        left_text = normalize_requirement_text(left.text)
        right_text = normalize_requirement_text(right.text)
        score, reason = _conflict_score(left_text, right_text, same_module)
        if score >= 0.55:
            rows.append({
                "requirement_id_a": left.requirement_id,
                "requirement_id_b": right.requirement_id,
                "module_a": left.module,
                "module_b": right.module,
                "conflict_score": round(score, 3),
                "conflict_reason": reason,
            })
    return pd.DataFrame(rows, columns=["requirement_id_a", "requirement_id_b", "module_a", "module_b", "conflict_score", "conflict_reason"])


def detect_duplicates(requirements: pd.DataFrame, threshold: float = 0.82) -> pd.DataFrame:
    """Find near-duplicate requirements by token Jaccard similarity."""
    rows: list[dict[str, object]] = []
    for left, right in itertools.combinations(requirements.itertuples(index=False), 2):
        if left.template_id == right.template_id:
            continue
        left_tokens = set(tokenize_requirement(left.text))
        right_tokens = set(tokenize_requirement(right.text))
        if not left_tokens or not right_tokens:
            continue
        similarity = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
        if similarity >= threshold:
            rows.append({"requirement_id_a": left.requirement_id, "requirement_id_b": right.requirement_id, "similarity": round(similarity, 3), "duplicate_reason": "high token overlap"})
    return pd.DataFrame(rows, columns=["requirement_id_a", "requirement_id_b", "similarity", "duplicate_reason"])


def _conflict_score(left_text: str, right_text: str, same_module: bool) -> tuple[float, str]:
    module_boost = 0.15 if same_module else 0.0
    for phrase_a, phrase_b in CONFLICT_PATTERNS:
        if phrase_a in left_text and phrase_b in right_text:
            return min(1.0, 0.75 + module_boost), f"opposing policy: '{phrase_a}' vs '{phrase_b}'"
        if phrase_b in left_text and phrase_a in right_text:
            return min(1.0, 0.75 + module_boost), f"opposing policy: '{phrase_b}' vs '{phrase_a}'"
    if ("shall not" in left_text and _shared_object(left_text, right_text)) or ("shall not" in right_text and _shared_object(left_text, right_text)):
        return min(1.0, 0.55 + module_boost), "negated requirement overlaps with related requirement"
    return 0.0, ""


def _shared_object(left_text: str, right_text: str) -> bool:
    key_terms = {"card", "password", "token", "profile", "backup", "login", "reset", "payment"}
    return bool(set(tokenize_requirement(left_text)) & set(tokenize_requirement(right_text)) & key_terms)
