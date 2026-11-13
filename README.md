# JBI100 Visualization project: Global Power Plant Database

Group project for JBI100 Visualization (TU/e, 2026-27). Data: Global Power Plant Database v1.3.0 by WRI (CC BY 4.0), in `data/` with its data dictionary `data/README.txt`.

## Setup

Requires Python 3.10 or later.

```
python -m venv venv
venv\Scripts\activate          (Windows)
source venv/bin/activate       (macOS/Linux)
pip install -r requirements.txt
```

## Assignment 1, Exercise 1 (c), (d), (f)

```
python assignment1.py            prints the analysis, writes CSV tables to output/a1/
python assignment1.py --plots    also writes one HTML chart per attribute to output/a1/plots/
```

| Part | Code | Output in `output/a1/` |
|---|---|---|
| (c) parsing | `powerplants/parsing.py`: `load_data()`, `get_value(df, row, column)` | printed |
| (d) distributions and frequencies | `powerplants/distribution.py`: `frequencies()`, `numeric_summary()`, `distribution_report()`, `plot_distributions()` | `attribute_overview.csv`, `numeric_summary.csv`, `frequencies/`, `histograms/`, `plots/` |
| (f) missing values and errors | `powerplants/missing.py`: `missing_per_attribute()`, `missing_per_entry()`, `missing_by_group()`, `find_errors()` | `missing_*.csv`, `errors_summary.csv`, `errors/` |

`output/` is generated and not committed.

## Own work, libraries and AI use

Libraries: pandas, NumPy, Plotly (via Dash).

AI: Claude (Anthropic, Claude Opus 5.5) wrote the first version of `powerplants/` (parsing, distribution, missing) and `assignment1.py` for Assignment 1, Exercise 1 (c), (d), (f). The group reviewed it. The written answers for Assignment 1 are the group's own.
