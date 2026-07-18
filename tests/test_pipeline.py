import json
import subprocess
import sys


def test_synthetic_pipeline_smoke(tmp_path):
    output_dir = tmp_path / "outputs"
    cmd = [
        sys.executable,
        "scripts/run_synthetic_requirements_lab.py",
        "--repeat-templates",
        "1",
        "--seed",
        "11",
        "--output-dir",
        str(output_dir),
    ]
    subprocess.run(cmd, check=True)
    summary_path = output_dir / "results" / "synthetic_requirements_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["requirement_count"] >= 10
    assert summary["conflict_pair_count"] > 0
    assert summary["audit_log"]["valid"] is True
