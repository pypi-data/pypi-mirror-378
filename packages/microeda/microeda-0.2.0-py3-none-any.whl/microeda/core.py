from __future__ import annotations
import math
from typing import Any, Dict, Optional
from collections import Counter

import numpy as np # type: ignore
import pandas as pd # type: ignore

# ---------- utils ----------
def is_temporal_series(s: pd.Series, sample_size: int = 100) -> bool:
    """Heuristically check if a Series is datetime-like."""
    if pd.api.types.is_datetime64_any_dtype(s):
        return True
    non_null = s.dropna().astype(str)
    if non_null.empty:
        return False
    sample = non_null.sample(min(len(non_null), sample_size), random_state=1)
    success = sum(pd.to_datetime(v, errors="coerce") is not pd.NaT for v in sample)
    return (success / len(sample)) > 0.9


def try_cast_numeric(s: pd.Series, tol: float = 0.95) -> bool:
    """Check if Series can mostly be cast to numeric."""
    non_na = s.dropna()
    if non_na.empty:
        return False
    converted = pd.to_numeric(non_na, errors="coerce")
    return converted.notna().mean() >= tol


# ---------- column typing ----------
def detect_column_type(s: pd.Series) -> str:
    """
    Heuristically detect a column's semantic type.
    Returns: "boolean", "numeric", "datetime", "text", "id", or "categorical".
    """
    if pd.api.types.is_bool_dtype(s):
        return "boolean"
    if pd.api.types.is_integer_dtype(s) or pd.api.types.is_float_dtype(s):
        return "numeric"
    if is_temporal_series(s):
        return "datetime"
    if try_cast_numeric(s):
        return "numeric" if s.nunique(dropna=True) > 20 else "categorical"

    avg_len = s.dropna().astype(str).map(len).mean() if len(s.dropna()) else 0
    uniq = s.nunique(dropna=True)
    if avg_len > 50 or uniq / max(1, len(s)) > 0.5:
        return "text"
    if uniq == len(s.dropna()) and uniq > 20:
        return "id"
    return "categorical"


# ---------- summarizers ----------
def summarize_numeric(s: pd.Series) -> Dict[str, Any]:
    arr = pd.to_numeric(s, errors="coerce").dropna()
    if arr.empty:
        return {"count": 0}
    desc = {
        "count": int(arr.count()),
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "min": float(arr.min()),
        "25%": float(arr.quantile(0.25)),
        "50%": float(arr.median()),
        "75%": float(arr.quantile(0.75)),
        "max": float(arr.max()),
        "n_missing": int(s.isna().sum()),
        "n_unique": int(s.nunique(dropna=True)),
    }
    return desc


def summarize_categorical(s: pd.Series, topk: int = 6) -> Dict[str, Any]:
    arr = s.dropna().astype(str)
    vc = arr.value_counts().head(topk).to_dict()
    return {
        "count": int(arr.count()),
        "n_missing": int(s.isna().sum()),
        "n_unique": int(arr.nunique()),
        "top_values": {k: int(v) for k, v in vc.items()},
    }


def summarize_datetime(s: pd.Series) -> Dict[str, Any]:
    ser = pd.to_datetime(s, errors="coerce")
    non_null = ser.dropna()
    desc = {"count": int(non_null.count())}
    if non_null.empty:
        return desc
    desc.update(
        {
            "min": str(non_null.min()),
            "max": str(non_null.max()),
            "n_missing": int(s.isna().sum()),
            "n_unique": int(non_null.nunique()),
        }
    )
    return desc


def summarize_text(s: pd.Series, topk: int = 10) -> Dict[str, Any]:
    arr = s.dropna().astype(str)
    token_counts = arr.map(lambda x: len(x.split()))
    words = Counter()
    for t in arr:
        for w in t.lower().split():
            w = "".join(ch for ch in w if ch.isalnum())
            if len(w) > 1:
                words[w] += 1
    return {
        "count": int(arr.count()),
        "n_missing": int(s.isna().sum()),
        "n_unique": int(arr.nunique()),
        "avg_tokens": float(token_counts.mean()) if not token_counts.empty else 0.0,
        "top_words": dict(words.most_common(topk)),
    }


# ---------- Missingness ----------
def missingness_summary(df: pd.DataFrame, topk: int = 10) -> Dict[str, Any]:
    n = len(df)
    res: Dict[str, Any] = {"total_rows": int(n)}
    per_col = (df.isna().sum() / max(1, n)).sort_values(ascending=False)
    res["per_column_percent_missing"] = (per_col * 100).round(2).to_dict()

    cols = df.columns.tolist()
    pair_scores = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            a = df[cols[i]].isna().astype(int)
            b = df[cols[j]].isna().astype(int)
            if a.sum() == 0 or b.sum() == 0:
                continue
            cont = pd.crosstab(a, b)
            if cont.shape != (2, 2):
                continue
            n11, n10, n01, n00 = cont.iloc[1, 1], cont.iloc[1, 0], cont.iloc[0, 1], cont.iloc[0, 0]
            num = n11 * n00 - n10 * n01
            den = math.sqrt((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00))
            score = float(num / den) if den != 0 else 0.0
            pair_scores.append(((cols[i], cols[j]), score))
    pair_scores.sort(key=lambda x: abs(x[1]), reverse=True)
    res["top_missing_correlations"] = [(a, b, round(s, 3)) for (a, b), s in pair_scores[:topk]]
    return res


# ---------- Outlier detection ----------
def detect_outliers_iqr(s: pd.Series) -> Dict[str, Any]:
    arr = pd.to_numeric(s, errors="coerce").dropna()
    if arr.empty:
        return {"n_outliers": 0}
    q1, q3 = arr.quantile(0.25), arr.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    n_out = int(((arr < low) | (arr > high)).sum())
    return {"n_outliers": n_out, "iqr_low": float(low), "iqr_high": float(high)}


def detect_outliers_zscore(s: pd.Series, threshold: float = 3.0) -> Dict[str, Any]:
    arr = pd.to_numeric(s, errors="coerce").dropna()
    if arr.empty:
        return {"n_outliers": 0}
    std = arr.std()
    if std == 0:
        return {"n_outliers": 0}
    z = ((arr - arr.mean()) / std).abs()
    return {"n_outliers": int((z > threshold).sum())}


# ---------- Pairwise metrics ----------
def _discretize_numeric(arr: np.ndarray, bins: int = 10) -> np.ndarray:
    try:
        quantiles = np.linspace(0, 1, bins + 1)
        edges = np.quantile(arr[~np.isnan(arr)], quantiles)
        edges = np.unique(edges)
        if len(edges) <= 1:
            return np.zeros_like(arr, dtype=int)
        return np.digitize(arr, edges[1:-1], right=True)
    except Exception:
        return np.zeros_like(arr, dtype=int)


def _entropy(counts: np.ndarray) -> float:
    ps = counts / counts.sum()
    ps = ps[ps > 0]
    return -np.sum(ps * np.log2(ps))


def mutual_information(x: pd.Series, y: pd.Series, bins: int = 10) -> float:
    xa, ya = x.dropna().astype(str), y.dropna().astype(str)
    joined = pd.concat([xa, ya], axis=1).dropna()
    if joined.empty:
        return 0.0
    xj, yj = joined.iloc[:, 0], joined.iloc[:, 1]
    try:
        xnum = pd.to_numeric(xj, errors="coerce")
        ynum = pd.to_numeric(yj, errors="coerce")
        if xnum.notna().sum() > 0 and ynum.notna().sum() > 0:
            xdisc = _discretize_numeric(xnum.values, bins=bins)
            ydisc = _discretize_numeric(ynum.values, bins=bins)
        else:
            xdisc, ydisc = pd.factorize(xj)[0], pd.factorize(yj)[0]
    except Exception:
        xdisc, ydisc = pd.factorize(xj)[0], pd.factorize(yj)[0]
    pairs = list(zip(xdisc, ydisc))
    c_xy, c_x, c_y = Counter(pairs), Counter(xdisc), Counter(ydisc)
    h_x = _entropy(np.array(list(c_x.values())))
    h_y = _entropy(np.array(list(c_y.values())))
    h_xy = _entropy(np.array(list(c_xy.values())))
    return float(max(0.0, h_x + h_y - h_xy))


def cramers_v(x: pd.Series, y: pd.Series) -> float:
    a, b = x.dropna().astype(str), y.dropna().astype(str)
    joined = pd.concat([a, b], axis=1).dropna()
    if joined.empty:
        return 0.0
    ct = pd.crosstab(joined.iloc[:, 0], joined.iloc[:, 1])
    mean = ct.values.mean()
    chi2 = (((ct - mean) ** 2) / (mean + 1e-9)).sum()
    n = ct.values.sum()
    phi2 = chi2 / n
    r, k = ct.shape
    denom = min(k - 1, r - 1)
    return 0.0 if denom == 0 else float(math.sqrt(phi2 / denom))


def pairwise_hints(df: pd.DataFrame, types: Dict[str, str], topk: int = 10) -> Dict[str, Any]:
    cols = df.columns.tolist()
    results = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            a, b = cols[i], cols[j]
            ta, tb = types[a], types[b]
            score, metric = None, None
            try:
                if ta == tb == "numeric":
                    aa = pd.to_numeric(df[a], errors="coerce")
                    bb = pd.to_numeric(df[b], errors="coerce")
                    joined = pd.concat([aa, bb], axis=1).dropna()
                    if len(joined) > 2:
                        corr = joined.iloc[:, 0].corr(joined.iloc[:, 1])
                        score = 0.0 if pd.isna(corr) else float(corr)
                        metric = "pearson"
                elif ta == "numeric" and tb in ("categorical", "boolean") or \
                     tb == "numeric" and ta in ("categorical", "boolean"):
                    score = mutual_information(df[a], df[b])
                    metric = "mutual_info"
                else:
                    score = cramers_v(df[a], df[b])
                    metric = "cramers_v"
            except Exception:
                score = None
            if score is not None:
                results.append(((a, b), metric, float(score)))
    results.sort(key=lambda x: abs(x[2]) if x[2] is not None else 0.0, reverse=True)
    return {"pairs": [(a, b, m, round(s, 4)) for (a, b), m, s in results[:topk]]}


# ---------- main engine ----------
def analyze(df: pd.DataFrame,
            name: Optional[str] = None,
            config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Run full micro-EDA and return a nested dictionary with results.
    """
    if config is None:
        config = {}

    nrows, ncols = df.shape
    out: Dict[str, Any] = {
        "name": name or "dataset",
        "n_rows": int(nrows),
        "n_cols": int(ncols),
    }

    col_types: Dict[str, str] = {}
    summaries: Dict[str, Dict[str, Any]] = {}

    for col in df.columns:
        s = df[col]
        ctype = detect_column_type(s)
        col_types[col] = ctype

        if ctype == "numeric":
            desc = summarize_numeric(s)
            desc.update(detect_outliers_iqr(s))
        elif ctype in ("categorical", "boolean", "id"):
            desc = summarize_categorical(s)
        elif ctype == "datetime":
            desc = summarize_datetime(s)
        elif ctype == "text":
            desc = summarize_text(s)
        else:
            desc = {"count": int(s.count())}

        desc.update({
            "type": ctype,
            "n_missing": int(s.isna().sum()),
            "pct_missing": round(100 * s.isna().sum() / max(1, len(df)), 3),
            "n_unique": int(s.nunique(dropna=True)),
        })

        summaries[col] = desc

    out["column_types"] = col_types
    out["summaries"] = summaries
    out["missingness"] = missingness_summary(df)
    out["pairwise_hints"] = pairwise_hints(df, col_types, topk=20)
    out["global"] = {
        "n_null_rows": int(df.isna().all(axis=1).sum()),
        "cols_all_unique": [c for c in df.columns if df[c].nunique(dropna=True) == len(df)],
    }

    # Provide "columns" list for easier iteration
    out["columns"] = [
        {
            "name": col,
            "type": summaries[col]["type"],
            "missing_percent": summaries[col]["pct_missing"],
            **{k: v for k, v in summaries[col].items() if k != "pct_missing"},
        }
        for col in df.columns
    ]

    return out