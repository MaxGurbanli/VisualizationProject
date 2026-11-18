"""Start the dashboard: python app.py, then open the printed http link.

Layout and callback structure adapted from the course template
(https://gitlab.tue.nl/JBI100/dashframework).
"""

from dash import Input, Output, html

from dashboard import selection
from dashboard.data import get_data
from dashboard.main import app
from dashboard.views.menu import make_menu_layout
from dashboard.views.plant_map import make_plant_map
from dashboard.views.scatterplot import make_scatterplot


def build_app():
    df = get_data()
    views = [make_plant_map(df), make_scatterplot(df)]

    app.layout = html.Div(
        id="app-container",
        children=[
            selection.make_store(),
            html.Div(id="left-column", className="three columns",
                     children=make_menu_layout(len(df))),
            html.Div(id="right-column", className="nine columns", children=views),
        ],
    )

    # Linking: every view writes to and reads from the shared selection.
    selection.register_callbacks(app, views)

    @app.callback(Output("selection-count", "children"), Input(selection.STORE_ID, "data"))
    def show_count(sel):
        return "No selection" if sel is None else f"{len(sel['ids']):,} plants selected"

    return app


if __name__ == "__main__":
    build_app().run(debug=False, dev_tools_ui=False)
