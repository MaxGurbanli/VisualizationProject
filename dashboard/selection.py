"""Shared selection that links all views.

One dcc.Store holds the current selection: None when nothing is selected,
otherwise {"source": <graph id of the view brushed in>, "ids": [plant ids]}
with ids from data.KEY. Every view writes to it when the user brushes in that
view, and every view reads it to highlight the same plants. So linking is
multi-directional: a brush in any view highlights in all the others.

Adding a view:
  1. give its traces customdata=<plant id column>,
  2. add (component id, "selectedData") to the list passed to register_callbacks,
  3. give the view a highlight(selection) method that returns a dash.Patch
     (views/base.py does this for single-trace views).
"""

import time

from dash import Input, Output, State, ctx, dcc, no_update

STORE_ID = "selected-plants"
RESET_ID = "reset-selection"


def make_store():
    """The store component; put it once anywhere in the layout."""
    return dcc.Store(id=STORE_ID, data=None)


def ids_from_selected_data(selected_data):
    """Plant ids in a Plotly selectedData event, or None if the selection was cleared."""
    if not selected_data or not selected_data.get("points"):
        return None
    ids = {p["customdata"] for p in selected_data["points"] if "customdata" in p}
    return sorted(ids)


def register_callbacks(app, views, timing_log=None):
    """Wire the store to every view.

    views: list of view objects, each with .graph_id and .highlight(selection).
    timing_log: optional list; each callback appends (name, seconds) for testing speed.
    """

    @app.callback(
        Output(STORE_ID, "data"),
        [Input(v.graph_id, "selectedData") for v in views] + [Input(RESET_ID, "n_clicks")],
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def update_selection(*args):
        *selected_per_view, _reset_clicks, current = args
        # Only the input that fired matters: the latest brush replaces the selection.
        if ctx.triggered_id == RESET_ID:
            return None
        for view, selected_data in zip(views, selected_per_view):
            if view.graph_id != ctx.triggered_id:
                continue
            ids = ids_from_selected_data(selected_data)
            if ids is not None:
                return {"source": view.graph_id, "ids": ids}
            # An empty selection only clears the store when it comes from the view
            # that made the current selection (the user deselected there). When another
            # view is the source, the empty event is the side effect of highlight()
            # removing this view's old brush rectangle, and must be ignored, or a brush
            # in view A would be wiped out by view B straight away.
            if current is not None and current["source"] == view.graph_id:
                return None
            return no_update
        return no_update

    for view in views:
        _register_highlight(app, view, timing_log)


def _register_highlight(app, view, timing_log):
    # Separate function so each callback closes over its own view.
    @app.callback(
        Output(view.graph_id, "figure"),
        Input(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def highlight(selection):
        start = time.perf_counter()
        patch = view.highlight(selection)
        if timing_log is not None:
            timing_log.append((view.graph_id, time.perf_counter() - start))
        return patch
