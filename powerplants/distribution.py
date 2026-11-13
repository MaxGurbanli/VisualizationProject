"""Attribute distributions and value frequencies (Assignment 1, Exercise 1d)."""

from pathlib import Path

import numpy as np
import pandas as pd

from .parsing import ATTRIBUTE_GROUPS

# Heavy-tailed quantities (a few huge plants, many small ones): plot on a log axis.
_LOG_SCALE = set(ATTRIBUTE_GROUPS["quantitative"])

# Text columns with more distinct values than this get a top-N table only.
MAX_FULL_TABLE = 250


def frequencies(series, top=None):
    """Count how often each value occurs, including NA, with percentages.

    Returns a DataFrame with columns value, count, percent, sorted by count.
    top: keep only the `top` most frequent values (None keeps all).
    """
    counts = series.value_counts(dropna=False)
    table = pd.DataFrame({
        "value": counts.index.astype(object),
        "count": counts.values,
        "percent": (100 * counts.values / len(series)).round(2),
    })
    # Show NA as a readable label instead of <NA>/nan.
    table["value"] = table["value"].where(table["value"].notna(), "(missing)")
    return table.head(top) if top else table


def numeric_summary(series, bins=20):
    """Summary statistics and a binned histogram for a numeric attribute.

    Returns (stats, histogram): stats is a Series (count, missing, min, quartiles,
    max, mean, std, skew); histogram is a DataFrame with bin_left, bin_right, count.
    """
    values = series.dropna()
    stats = pd.Series({
        "count": len(values),
        "missing": series.isna().sum(),
        "min": values.min(),
        "q1": values.quantile(0.25),
        "median": values.median(),
        "q3": values.quantile(0.75),
        "max": values.max(),
        "mean": values.mean(),
        "std": values.std(),
        "skew": values.skew(),
    }, name=series.name)
    if len(values) == 0:
        return stats, pd.DataFrame(columns=["bin_left", "bin_right", "count"])
    counts, edges = np.histogram(values, bins=bins)
    histogram = pd.DataFrame({"bin_left": edges[:-1], "bin_right": edges[1:], "count": counts})
    return stats, histogram


def attribute_kind(column):
    """Name of the ATTRIBUTE_GROUPS group a column belongs to."""
    for kind, cols in ATTRIBUTE_GROUPS.items():
        if column in cols:
            return kind
    return "other"


def distribution_report(df, top=15):
    """Distribution of every attribute, chosen by attribute kind.

    Returns a dict column -> dict with:
        kind        attribute group
        n_unique    number of distinct non-missing values
        missing     number of missing values
        stats, histogram   (numeric columns only)
        frequencies        (all columns; top values only for identifiers/text)
    """
    report = {}
    for col in df.columns:
        series = df[col]
        kind = attribute_kind(col)
        entry = {"kind": kind, "n_unique": series.nunique(dropna=True), "missing": int(series.isna().sum())}
        if pd.api.types.is_numeric_dtype(series):
            entry["stats"], entry["histogram"] = numeric_summary(series)
            # Years have few distinct values, so their exact frequencies are useful too.
            if kind == "temporal":
                entry["frequencies"] = frequencies(series.round(), top=None)
        elif kind == "identifier" or entry["n_unique"] > MAX_FULL_TABLE:
            # Many distinct values (names, ids, urls, owners): a full table is
            # mostly values that occur once, so keep only the most frequent.
            entry["frequencies"] = frequencies(series, top=top)
        else:
            entry["frequencies"] = frequencies(series)
        report[col] = entry
    return report


def plot_distributions(df, out_dir, columns=None):
    """Write one interactive Plotly HTML chart per attribute to out_dir.

    Categorical columns: horizontal bar chart of the 30 most frequent values.
    Numeric columns: histogram, log-scaled x axis for capacity/generation.
    Identifier columns are skipped. Returns the list of written files.
    """
    import plotly.express as px  # imported here so the rest works without plotly

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for col in columns or df.columns:
        kind = attribute_kind(col)
        if kind == "identifier" or col in ("url", "owner", "name"):
            continue
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            values = series.dropna()
            if col in _LOG_SCALE:
                values = values[values > 0]  # log axis cannot show zero or negative values
                fig = px.histogram(x=np.log10(values), nbins=60,
                                   labels={"x": f"log10({col})", "count": "plants"},
                                   title=f"{col} (log10, {series.isna().sum()} missing, non-positive values dropped)")
            else:
                fig = px.histogram(x=values, nbins=60, labels={"x": col},
                                   title=f"{col} ({series.isna().sum()} missing)")
        else:
            table = frequencies(series, top=30).iloc[::-1]  # largest at the top of the chart
            fig = px.bar(table, x="count", y="value", orientation="h",
                         title=f"{col}: 30 most frequent values (of {series.nunique()})")
            fig.update_yaxes(type="category", title=None)
        path = out_dir / f"{col}.html"
        fig.write_html(path, include_plotlyjs="cdn")
        written.append(path)
    return written
