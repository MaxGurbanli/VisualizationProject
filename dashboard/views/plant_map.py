"""PLACEHOLDER view: every plant as a point on a world map.

Only here to test linking and speed on the full data. Whether and how the tool
shows geography is a group design decision still to be made.

Highlighting works differently from the other views. Updating `selectedpoints`
on a Scattermap trace through a Dash Patch renders unreliably (tested 18 Nov
2026 with plotly 7.1: sometimes the wrong points, sometimes no dimming). So the
map has two traces: trace 0 holds all plants and is only dimmed, trace 1 holds
only the selected plants, drawn on top. The patch sends just the selected
coordinates, so its size grows with the selection, not with the data.
"""

from itertools import count

import plotly.graph_objects as go
from dash import Patch

from ..config import SELECTED_COLOR, UNSELECTED_COLOR, UNSELECTED_OPACITY
from ..data import KEY
from .base import LinkedView


_revision = count(1)


class PlantMap(LinkedView):
    def build_figure(self, df):
        fig = go.Figure()
        fig.add_trace(go.Scattermap(  # trace 0: all plants (MapLibre map, no access token needed)
            lat=df["latitude"],
            lon=df["longitude"],
            customdata=df[KEY],
            mode="markers",
            marker=dict(size=4, color=SELECTED_COLOR, opacity=1.0),
            text=df["name"],
            hovertemplate="%{text}<br>%{customdata}<extra></extra>",
            showlegend=False,
        ))
        fig.add_trace(go.Scattermap(  # trace 1: selected plants, empty until something is selected
            lat=[], lon=[], customdata=[], text=[],
            mode="markers",
            marker=dict(size=5, color=SELECTED_COLOR),
            hovertemplate="%{text}<br>%{customdata}<extra></extra>",
            showlegend=False,
        ))
        fig.update_layout(
            dragmode="select",
            margin=dict(l=0, r=0, t=0, b=0),
            map=dict(style="carto-positron", zoom=1, center=dict(lat=20, lon=0)),
        )
        return fig

    def highlight(self, selection):
        patch = Patch()
        if selection is None:
            patch["data"][0]["marker"]["color"] = SELECTED_COLOR
            patch["data"][0]["marker"]["opacity"] = 1.0
            subset = self.df.iloc[0:0]
            patch["layout"]["selections"] = []
        else:
            patch["data"][0]["marker"]["color"] = UNSELECTED_COLOR
            patch["data"][0]["marker"]["opacity"] = UNSELECTED_OPACITY
            positions = sorted(self.position[p] for p in selection["ids"] if p in self.position)
            subset = self.df.iloc[positions]
            if selection["source"] != self.graph_id:
                patch["layout"]["selections"] = []
        # Plotly's own selection state on trace 0 is cleared so only the overlay shows it.
        patch["data"][0]["selectedpoints"] = None
        patch["data"][1]["selectedpoints"] = None
        patch["data"][1]["lat"] = subset["latitude"].tolist()
        patch["data"][1]["lon"] = subset["longitude"].tolist()
        patch["data"][1]["customdata"] = subset[KEY].tolist()
        patch["data"][1]["text"] = subset["name"].tolist()
        # Dash applies the patch to the stored figure in place, so Plotly's diff can
        # miss the change on a map; a new datarevision forces the redraw.
        patch["layout"]["datarevision"] = next(_revision)
        return patch


def make_plant_map(df):
    return PlantMap("Placeholder map", df)
