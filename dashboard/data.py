"""Data for the dashboard: loaded once at start-up and shared by all views."""

from functools import lru_cache

from powerplants.parsing import load_data

# Column that identifies a plant. Every view passes it to Plotly as customdata,
# so a selection is a set of plant ids and not a set of point positions.
# Positions differ per view (a view may drop plants with missing values),
# ids do not.
KEY = "gppd_idnr"


def prepare(df):
    """Hook for preprocessing (missing values, errors, derived attributes).

    Left empty on purpose: how missing values and errors are handled is
    Assignment 1, exercise 3, and is decided by the group. Plug it in here.
    """
    return df


@lru_cache(maxsize=1)
def get_data():
    """Return the prepared DataFrame. Cached, so the CSV is read only once."""
    return prepare(load_data())
