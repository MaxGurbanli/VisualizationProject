"""Assignment 1, Exercise 1 (c), (d), (f) on the Global Power Plant Database.

Usage:
    python assignment1.py            print summaries, write CSV tables to output/a1/
    python assignment1.py --plots    also write one HTML chart per attribute to output/a1/plots/
"""

import argparse
from pathlib import Path

import pandas as pd

from powerplants.distribution import distribution_report, plot_distributions
from powerplants.missing import (error_summary, find_errors, missing_by_group,
                                 missing_per_attribute, missing_per_entry)
from powerplants.parsing import get_value, load_data

OUT = Path(__file__).resolve().parent / "output" / "a1"

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 20)
pd.set_option("display.max_rows", 60)


def heading(text):
    print(f"\n{'=' * 78}\n{text}\n{'=' * 78}")


def part_c(df):
    """(c) Parsing: shape, column types and reading single (row, column) positions."""
    heading("(c) Parsing")
    print(f"{df.shape[0]} rows (plants) x {df.shape[1]} columns")
    print("\nColumn types:")
    print(df.dtypes.astype(str).value_counts().to_string())
    print("\nExamples of get_value(df, row, column):")
    for row, col in [(0, "name"), (0, "capacity_mw"), (1, 7), (len(df) - 1, "country_long")]:
        print(f"  get_value(df, {row}, {col!r}) = {get_value(df, row, col)!r}")


def part_d(df):
    """(d) Distribution of every attribute and the frequency of its values."""
    heading("(d) Distributions and frequencies")
    report = distribution_report(df)
    freq_dir, hist_dir = OUT / "frequencies", OUT / "histograms"
    freq_dir.mkdir(parents=True, exist_ok=True)
    hist_dir.mkdir(parents=True, exist_ok=True)

    # Overview: one line per attribute.
    overview = pd.DataFrame({
        col: {"kind": e["kind"], "n_unique": e["n_unique"], "missing": e["missing"]}
        for col, e in report.items()
    }).T
    print(overview.to_string())
    overview.to_csv(OUT / "attribute_overview.csv")

    # Numeric attributes: summary statistics in one table.
    stats = pd.DataFrame([e["stats"] for e in report.values() if "stats" in e])
    print("\nNumeric attributes:")
    print(stats.round(2).to_string())
    stats.to_csv(OUT / "numeric_summary.csv")

    # Frequency tables: print the main categorical ones, save all of them.
    for col in ["primary_fuel", "country_long", "commissioning_year", "estimated_generation_note_2017"]:
        print(f"\nTop 10 values of {col}:")
        print(report[col]["frequencies"].head(10).to_string(index=False))
    for col, e in report.items():
        if "frequencies" in e:
            e["frequencies"].to_csv(freq_dir / f"{col}.csv", index=False)
        if "histogram" in e:
            e["histogram"].to_csv(hist_dir / f"{col}.csv", index=False)
    print(f"\nAll frequency tables and histograms written to {OUT}")


def part_f(df):
    """(f) Missing values per attribute and per entry, plus error checks."""
    heading("(f) Missing values and errors")
    per_attr = missing_per_attribute(df)
    print("Missing values per attribute:")
    print(per_attr.to_string())
    per_attr.to_csv(OUT / "missing_per_attribute.csv")

    per_row, dist = missing_per_entry(df)
    print("\nMissing values per entry (how many plants miss k of the 36 fields):")
    print(dist.to_string(index=False))
    print(f"Mean missing fields per plant: {per_row.mean():.1f}")
    per_row.to_csv(OUT / "missing_per_entry.csv")
    dist.to_csv(OUT / "missing_per_entry_distribution.csv", index=False)

    by_fuel = missing_by_group(df, by="primary_fuel")
    print("\n% missing per primary fuel:")
    print(by_fuel.to_string())
    by_fuel.to_csv(OUT / "missing_by_fuel.csv")

    by_country = missing_by_group(df, by="country_long")
    print("\n% missing for the 15 countries with most plants:")
    print(by_country.head(15).to_string())
    by_country.to_csv(OUT / "missing_by_country.csv")

    rules = find_errors(df)
    summary = error_summary(rules)
    print("\nError checks (rows violating each rule):")
    print(summary.to_string(index=False))
    summary.to_csv(OUT / "errors_summary.csv", index=False)
    err_dir = OUT / "errors"
    err_dir.mkdir(exist_ok=True)
    for i, (rule, rows) in enumerate(rules.items()):
        if len(rows):
            rows.to_csv(err_dir / f"rule{i:02d}.csv", index=False)
    print(f"Offending rows per rule written to {err_dir} (file number = row in the table above)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--plots", action="store_true", help="write one HTML chart per attribute")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    df = load_data()
    part_c(df)
    part_d(df)
    part_f(df)
    if args.plots:
        files = plot_distributions(df, OUT / "plots")
        print(f"\n{len(files)} charts written to {OUT / 'plots'}")


if __name__ == "__main__":
    main()
