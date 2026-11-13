"""Missing values and data errors (Assignment 1, Exercise 1f)."""

import pandas as pd

from .parsing import YEARS_ESTIMATED, YEARS_REPORTED

HOURS_PER_YEAR = 8760  # used for the capacity factor check: MW * h / 1000 = GWh


def missing_per_attribute(df):
    """Number and percentage of missing values per column, most missing first."""
    counts = df.isna().sum()
    table = pd.DataFrame({
        "missing": counts,
        "percent": (100 * counts / len(df)).round(2),
        "present": len(df) - counts,
    })
    return table.sort_values("missing", ascending=False)


def missing_per_entry(df, id_column="gppd_idnr"):
    """Missing values per row (plant).

    Returns (per_row, distribution):
        per_row       Series id -> number of missing fields in that row
        distribution  DataFrame: n_missing, n_rows, percent (how many plants miss k fields)
    """
    per_row = df.isna().sum(axis=1)
    per_row.index = df[id_column]
    per_row.name = "n_missing"
    dist = per_row.value_counts().sort_index()
    distribution = pd.DataFrame({
        "n_missing": dist.index,
        "n_rows": dist.values,
        "percent": (100 * dist.values / len(df)).round(2),
    })
    return per_row, distribution


def missing_by_group(df, by="primary_fuel", columns=None):
    """Percentage missing of `columns` within each group of `by`.

    Shows whether missingness is random or tied to a category (for example,
    reported generation exists only for a few countries).
    Default columns: commissioning_year, owner, generation_gwh_2017,
    estimated_generation_gwh_2017.
    """
    columns = columns or ["commissioning_year", "owner", "generation_gwh_2017",
                          "estimated_generation_gwh_2017"]
    grouped = df[columns].isna().groupby(df[by], observed=True).mean() * 100
    grouped.insert(0, "n_plants", df.groupby(by, observed=True).size())
    return grouped.round(1).sort_values("n_plants", ascending=False)


def find_errors(df):
    """Rule-based checks for values that are impossible or suspicious.

    Returns a dict rule -> DataFrame of offending rows (id, name, country and
    the columns involved). Missing values never count as errors here.
    """
    gen_cols = [f"generation_gwh_{y}" for y in YEARS_REPORTED]
    est_cols = [f"estimated_generation_gwh_{y}" for y in YEARS_ESTIMATED]
    base = ["gppd_idnr", "name", "country", "primary_fuel", "capacity_mw"]
    rules = {}

    def add(rule, mask, cols):
        rules[rule] = df.loc[mask.fillna(False), base + [c for c in cols if c not in base]]

    add("capacity_mw <= 0", df["capacity_mw"] <= 0, [])
    add("latitude outside [-90, 90]", ~df["latitude"].between(-90, 90) & df["latitude"].notna(), ["latitude"])
    add("longitude outside [-180, 180]", ~df["longitude"].between(-180, 180) & df["longitude"].notna(), ["longitude"])
    add("commissioning_year outside [1850, 2021]",
        ~df["commissioning_year"].between(1850, 2021) & df["commissioning_year"].notna(),
        ["commissioning_year"])
    add("commissioning_year after year_of_capacity_data",
        df["commissioning_year"] > df["year_of_capacity_data"],
        ["commissioning_year", "year_of_capacity_data"])
    add("negative reported generation", (df[gen_cols] < 0).any(axis=1), gen_cols)
    add("negative estimated generation", (df[est_cols] < 0).any(axis=1), est_cols)

    # A plant cannot produce more than capacity * hours in a year (capacity factor > 1).
    max_gwh = df["capacity_mw"] * HOURS_PER_YEAR / 1000
    over = df[gen_cols].gt(max_gwh, axis=0).any(axis=1)
    add("reported generation > capacity * 8760 h", over, gen_cols)
    over_est = df[est_cols].gt(max_gwh, axis=0).any(axis=1)
    add("estimated generation > capacity * 8760 h", over_est, est_cols)

    add("duplicate gppd_idnr", df["gppd_idnr"].duplicated(keep=False), [])
    add("duplicate (name, latitude, longitude)",
        df.duplicated(["name", "latitude", "longitude"], keep=False), ["latitude", "longitude"])
    return rules


def error_summary(rules):
    """Number of offending rows per rule, as a DataFrame."""
    return pd.DataFrame({"rule": list(rules), "n_rows": [len(v) for v in rules.values()]})
