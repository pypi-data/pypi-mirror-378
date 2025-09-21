import io
import csv
import tempfile
from pathlib import Path

import pytest
import numpy as np
import pandas as pd

import microeda.core as core
import microeda.report as report

# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------
def tiny_dataframe():
    """Create a tiny DataFrame for smoke tests."""
    return pd.DataFrame({
        "num": [1, 2, 3, np.nan],
        "cat": ["a", "b", "a", "b"],
        "dt":  pd.to_datetime(["2024-01-01", "2024-01-02", None, "2024-01-04"])
    })

# --------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------

def test_analyze_returns_expected_keys():
    df = tiny_dataframe()
    result = core.analyze(df, name="demo")
    # Check top-level keys
    for key in ("name", "n_rows", "n_cols", "columns"):
        assert key in result
    # Should match actual dimensions
    assert result["n_rows"] == len(df)
    assert result["n_cols"] == len(df.columns)

def test_column_typing_inference():
    df = tiny_dataframe()
    result = core.analyze(df)
    coltypes = {col["name"]: col["type"] for col in result["columns"]}
    assert coltypes["num"] == "numeric"
    assert coltypes["cat"] == "categorical"
    assert coltypes["dt"] == "datetime"

def test_report_markdown_contains_column_names():
    df = tiny_dataframe()
    summary = core.analyze(df)
    md = report.render_report(summary, style="md")
    # All column names should appear in the markdown output
    for col in df.columns:
        assert col in md

def test_cli_runs_and_creates_file(tmp_path: Path):
    # Write csv to temp file
    csv_path = tmp_path / "sample.csv"
    tiny_dataframe().to_csv(csv_path, index=False)

    # Output markdown file
    out_path = tmp_path / "report.md"

    # Use pytest's helper to run the CLI as a subprocess
    from subprocess import run
    result = run(["python", "-m", "microeda.cli", str(csv_path), "--style", "md", "--out", str(out_path)])
    assert result.returncode == 0
    assert out_path.exists()
    text = out_path.read_text()
    # sanity check: some column name should be inside
    assert "num" in text

def test_missing_values_flagged():
    df = pd.DataFrame({"x": [1, None, 3]})
    summary = core.analyze(df)
    col = summary["columns"][0]
    assert col["missing_percent"] > 0