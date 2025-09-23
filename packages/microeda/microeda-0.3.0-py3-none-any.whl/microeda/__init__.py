"""
microeda: Advanced Micro Exploratory Data Analysis (<10k rows)
Lightweight, dependency-light and CLI friendly.
"""
from .core import analyze, analyze_table
from .report import render_report

__all__ = ["analyze", "analyze_table", "render_report"]
__version__ = "0.3.0"  # bump version for the new release