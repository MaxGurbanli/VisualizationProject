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

## Dashboard (skeleton)

```
python app.py                    then open http://127.0.0.1:8050 in a browser
```

The first load reads the CSV once (about 2 s). The two views (a map and a scatterplot of capacity against estimated generation 2017) are placeholders that test linked brushing on all 34,936 plants. They are not design choices: idioms, attributes, scales and colours are still to be decided by the group.

| File | What it does |
|---|---|
| `app.py` | builds the layout, registers the callbacks, starts the server |
| `dashboard/main.py`, `config.py`, `assets/` | Dash app object, placeholder colours, CSS from the course template |
| `dashboard/data.py` | loads the data once via `powerplants.parsing.load_data()`; `prepare()` is the empty hook for missing-value handling (Assignment 1, ex. 3) |
| `dashboard/selection.py` | the shared selection: one `dcc.Store` with the ids (`gppd_idnr`) of the selected plants; a brush in any view writes it, every view reads it, so linking works in all directions |
| `dashboard/views/base.py` | `LinkedView`: a card with one graph; highlights the selection by sending a `dash.Patch`, not the whole figure |
| `dashboard/views/plant_map.py`, `scatterplot.py` | the two placeholder views |
| `dashboard/views/menu.py` | left column: title, description, "Clear selection", selection count |

How linking works, and how to add a view: see the docstring at the top of `dashboard/selection.py`. In short: pass the plant id as `customdata`, add the graph to the list in `app.py`, and give the view a `highlight(selection)` method (inherited from `LinkedView` for single-trace views).

Known issues found while testing (18 Nov 2026, Dash 4.5, Plotly 7.1):

- Selections are passed as plant ids, not as the template's `pointIndex`. Positions differ per view as soon as a view drops plants (the scatterplot leaves out 1,891 plants without a positive 2017 estimate), so `pointIndex` would highlight the wrong plants.
- On the map (`Scattermap`), updating `selectedpoints` through a patch did not render reliably: wrong plants or no dimming. The map instead uses a second trace for the selected plants and bumps `layout.datarevision`, so the redraw is forced.
- Clearing an old brush rectangle in one view makes Plotly send an empty selection from that view. `selection.py` ignores an empty selection unless it comes from the view that made the current selection, or a new brush would be wiped out at once.
- Speed on a laptop: callback round trips of 4 to 14 ms; responses up to about 120 KB for a few thousand selected plants, against about 1.9 MB to resend the whole map figure.

## Own work, libraries and AI use

Libraries: pandas, NumPy, Plotly, Dash. The dashboard structure (app object, left menu and right column layout, `graph_card` views, CSS in `dashboard/assets/`) is adapted from the course template https://gitlab.tue.nl/JBI100/dashframework.

AI: Claude (Anthropic, Claude Opus 5.5) wrote the first version of `powerplants/` (parsing, distribution, missing) and `assignment1.py` for Assignment 1, Exercise 1 (c), (d), (f). The group reviewed it. The written answers for Assignment 1 are the group's own.

AI: Claude (Anthropic, Claude Opus 5.5) wrote the dashboard skeleton (`app.py`, `dashboard/`): the data loading hook, the shared-selection linking, the `LinkedView` base class and the two placeholder views, and tested the linking in the browser. To be reviewed by the group.
