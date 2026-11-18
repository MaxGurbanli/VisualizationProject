"""Left column: title, description and controls (adapted from the course template)."""

from dash import html

from ..selection import RESET_ID


def generate_description_card(n_plants):
    return html.Div(
        id="description-card",
        children=[
            html.H5("Global Power Plants"),
            html.Div(
                id="intro",
                children=(
                    f"Skeleton with {n_plants:,} plants. The two views are placeholders "
                    "that test linked brushing: select plants in one view and the same "
                    "plants are highlighted in the other."
                ),
            ),
        ],
    )


def generate_control_card():
    return html.Div(
        id="control-card",
        children=[
            html.Button("Clear selection", id=RESET_ID, n_clicks=0),
            html.Div(id="selection-count", style={"marginTop": "10px"}),
        ],
    )


def make_menu_layout(n_plants):
    return [generate_description_card(n_plants), generate_control_card()]
