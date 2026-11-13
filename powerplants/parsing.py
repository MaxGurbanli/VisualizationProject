"""Parsing of the Global Power Plant Database CSV (Assignment 1, Exercise 1c).

The file is UTF-8, comma separated, one header line, quotes only around text
that itself contains quotes (see data/README.txt). Empty fields mean "no value".
"""

from pathlib import Path

import pandas as pd

# Default location of the data file, relative to the repository root.
DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "global_power_plant_database.csv"

YEARS_REPORTED = range(2013, 2020)   # generation_gwh_2013 .. 2019
YEARS_ESTIMATED = range(2013, 2018)  # estimated_generation_gwh_2013 .. 2017

# Attribute groups, following the field list in data/README.txt.
# Used by the distribution and missing-value code, and as a starting point
# for the data abstraction table (Munzner "what").
ATTRIBUTE_GROUPS = {
    # unique keys / free text: frequency tables are not meaningful for these
    "identifier": ["gppd_idnr", "name", "wepp_id"],
    # categorical attributes (nominal)
    "categorical": [
        "country", "country_long", "primary_fuel",
        "other_fuel1", "other_fuel2", "other_fuel3", "owner",
    ],
    # quantitative attributes
    "quantitative": (
        ["capacity_mw"]
        + [f"generation_gwh_{y}" for y in YEARS_REPORTED]
        + [f"estimated_generation_gwh_{y}" for y in YEARS_ESTIMATED]
    ),
    # spatial position (WGS84 decimal degrees)
    "spatial": ["latitude", "longitude"],
    # temporal (years; commissioning_year is capacity-weighted, so can be fractional)
    "temporal": ["commissioning_year", "year_of_capacity_data"],
    # provenance: where the data came from and how generation was estimated
    "provenance": (
        ["source", "url", "geolocation_source", "generation_data_source"]
        + [f"estimated_generation_note_{y}" for y in YEARS_ESTIMATED]
    ),
}

# The 36 columns in file order, as documented in data/README.txt.
EXPECTED_COLUMNS = (
    ["country", "country_long", "name", "gppd_idnr", "capacity_mw",
     "latitude", "longitude", "primary_fuel", "other_fuel1", "other_fuel2",
     "other_fuel3", "commissioning_year", "owner", "source", "url",
     "geolocation_source", "wepp_id", "year_of_capacity_data"]
    + [f"generation_gwh_{y}" for y in YEARS_REPORTED]
    + ["generation_data_source"]
    + [f"estimated_generation_gwh_{y}" for y in YEARS_ESTIMATED]
    + [f"estimated_generation_note_{y}" for y in YEARS_ESTIMATED]
)

# Low-cardinality text columns are stored as pandas categories (less memory,
# and value_counts lists every category). Everything else that is text is a string.
_CATEGORY_COLUMNS = {
    "country", "country_long", "primary_fuel", "other_fuel1", "other_fuel2",
    "other_fuel3", "source", "geolocation_source", "generation_data_source",
    *[f"estimated_generation_note_{y}" for y in YEARS_ESTIMATED],
}
_NUMERIC_COLUMNS = set(
    ATTRIBUTE_GROUPS["quantitative"] + ATTRIBUTE_GROUPS["spatial"] + ATTRIBUTE_GROUPS["temporal"]
)


def _dtype_map():
    """Explicit dtype per column, so pandas never has to guess (e.g. wepp_id stays text)."""
    dtypes = {}
    for col in EXPECTED_COLUMNS:
        if col in _NUMERIC_COLUMNS:
            dtypes[col] = "float64"
        elif col in _CATEGORY_COLUMNS:
            dtypes[col] = "category"
        else:
            dtypes[col] = "string"
    return dtypes


def load_data(path=DEFAULT_PATH):
    """Read the power plant CSV into a DataFrame with one row per plant.

    Empty fields become NA. Raises ValueError if the header does not match the
    documented 36 columns, so a wrong or changed file is caught early.
    """
    df = pd.read_csv(path, dtype=_dtype_map(), encoding="utf-8", keep_default_na=False,
                     na_values=[""])
    if list(df.columns) != EXPECTED_COLUMNS:
        missing = set(EXPECTED_COLUMNS) - set(df.columns)
        extra = set(df.columns) - set(EXPECTED_COLUMNS)
        raise ValueError(f"Unexpected header. Missing: {sorted(missing)}, extra: {sorted(extra)}")
    return df


def get_value(df, row, column):
    """Return the value at a (row, column) position.

    row:    0-based row position (0 is the first plant, not the header).
    column: column name (e.g. "capacity_mw") or 0-based column position.
    """
    n_rows, n_cols = df.shape
    if not 0 <= row < n_rows:
        raise IndexError(f"row {row} out of range 0..{n_rows - 1}")
    if isinstance(column, int):
        if not 0 <= column < n_cols:
            raise IndexError(f"column {column} out of range 0..{n_cols - 1}")
        return df.iat[row, column]
    if column not in df.columns:
        raise KeyError(f"unknown column {column!r}")
    return df.iat[row, df.columns.get_loc(column)]
