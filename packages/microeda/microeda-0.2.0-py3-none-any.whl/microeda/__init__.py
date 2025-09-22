"""
microeda: Advanced Micro Exploratory Data Analysis (<10k rows)
Lightweight, dependency-light and CLI friendly.
"""
from .core import analyze
from .report import render_report
__all__ = ["analyze", "render_report"]
__version__ = "0.1.0"