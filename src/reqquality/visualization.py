"""Matplotlib figures for requirement-quality outputs."""

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def plot_quality_by_module(module_summary: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(module_summary["module"], module_summary["mean_quality_index"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Mean quality index")
    ax.set_title("Requirement quality by module")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_issue_counts(checks: pd.DataFrame, path: str | Path) -> None:
    issue_counts = {
        "Ambiguous": int((checks["ambiguous_term_count"] > 0).sum()),
        "Missing AC": int(checks["missing_acceptance_criteria"].sum()),
        "Missing test": int(checks["missing_test_case"].sum()),
        "Unverifiable": int(checks["unverifiable_statement"].sum()),
        "Risk flags": int(checks["security_privacy_risk"].sum()),
    }
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(list(issue_counts), list(issue_counts.values()))
    ax.set_ylabel("Requirement count")
    ax.set_title("Detected requirements quality issues")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_quality_distribution(scores: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(scores["requirement_quality_index"], bins=8)
    ax.set_xlabel("Requirement quality index")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of requirement quality")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_conflict_matrix(conflicts: pd.DataFrame, requirements: pd.DataFrame, path: str | Path) -> None:
    modules = sorted(requirements["module"].unique())
    matrix = pd.DataFrame(0, index=modules, columns=modules)
    for row in conflicts.itertuples(index=False):
        matrix.loc[row.module_a, row.module_b] += 1
        matrix.loc[row.module_b, row.module_a] += 1
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(matrix.values)
    ax.set_xticks(range(len(modules)), modules, rotation=45, ha="right")
    ax.set_yticks(range(len(modules)), modules)
    ax.set_title("Potential conflict matrix by module")
    for i in range(len(modules)):
        for j in range(len(modules)):
            ax.text(j, i, int(matrix.iloc[i, j]), ha="center", va="center")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_review_priority(scores: pd.DataFrame, path: str | Path) -> None:
    counts = scores["review_priority"].value_counts().reindex(["low", "medium", "high"], fill_value=0)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(counts.index, counts.values)
    ax.set_ylabel("Requirement count")
    ax.set_title("Review priority distribution")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
