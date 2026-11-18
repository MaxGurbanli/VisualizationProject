"""Base class for a view with one trace of plants, linked through the shared selection."""

from dash import Patch, dcc, html

from ..data import KEY


class LinkedView(html.Div):
    """A card with a title and one dcc.Graph whose single trace shows plants.

    Subclasses implement build_figure(df) and must give the trace customdata=df[KEY].
    The figure is built once; afterwards only the highlighting changes, sent as a
    dash.Patch so the browser receives the changed indices, not all points again.
    """

    def __init__(self, name, df):
        self.graph_id = name.lower().replace(" ", "-")
        self.df = df.reset_index(drop=True)
        # Plant id -> position of its point in the trace, to turn ids into selectedpoints.
        self.position = {pid: i for i, pid in enumerate(self.df[KEY])}
        self.figure = self.build_figure(self.df)
        super().__init__(
            className="graph_card",
            children=[html.H6(name), dcc.Graph(id=self.graph_id, figure=self.figure)],
        )

    def build_figure(self, df):
        raise NotImplementedError

    def highlight(self, selection):
        """Patch that highlights the selected plants in this view.

        selection: None, or {"source": graph id, "ids": [plant ids]} (see selection.py).
        Plants this view does not show (e.g. dropped for missing values) are ignored.
        """
        patch = Patch()
        if selection is None:
            patch["data"][0]["selectedpoints"] = None  # no selection: every mark normal
            patch["layout"]["selections"] = []
            return patch
        positions = [self.position[pid] for pid in selection["ids"] if pid in self.position]
        patch["data"][0]["selectedpoints"] = positions
        if selection["source"] != self.graph_id:
            # A brush in another view replaces any old brush rectangle here.
            patch["layout"]["selections"] = []
        return patch
