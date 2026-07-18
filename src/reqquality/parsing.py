"""Requirement parsing and normalization utilities."""

from __future__ import annotations

import re
import pandas as pd


def normalize_requirement_text(text: str) -> str:
    """Lowercase and normalize whitespace for rule-based analysis."""
    return re.sub(r"\s+", " ", str(text).strip().lower())


def tokenize_requirement(text: str) -> list[str]:
    """Tokenize a requirement into simple word tokens."""
    return re.findall(r"[a-zA-Z0-9_]+", normalize_requirement_text(text))


def classify_modality(text: str) -> str:
    """Classify normative strength."""
    normalized = normalize_requirement_text(text)
    if " shall " in f" {normalized} " or " must " in f" {normalized} ":
        return "mandatory"
    if " should " in f" {normalized} ":
        return "recommended"
    if " may " in f" {normalized} ":
        return "optional"
    return "unspecified"


def parse_requirement_table(requirements: pd.DataFrame) -> pd.DataFrame:
    """Attach normalized text, token count, and modality columns."""
    out = requirements.copy()
    out["normalized_text"] = out["text"].map(normalize_requirement_text)
    out["token_count"] = out["normalized_text"].map(lambda text: len(tokenize_requirement(text)))
    out["modality"] = out["text"].map(classify_modality)
    return out
