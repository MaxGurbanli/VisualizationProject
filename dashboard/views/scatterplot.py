"""PLACEHOLDER view: scatterplot of capacity against estimated generation 2017.

Only here to test linking and speed on the full data. Which attributes, scales
and idiom the tool uses is a group design decision still to be made.
"""

import plotly.graph_objects as go

from ..config import SELECTED_COLOR, UNSELECTED_COLOR, UNSELECTED_OPACITY
from ..data import KEY
from .base import LinkedView

X = "capacity_mw"
Y = "estimated_generation_gwh_2017"


class Scatterplot(LinkedView):
    def build_figure(self, df):
        fig = go.Figure(go.Scattergl(  # WebGL: tens of thousands of points stay responsive
            x=df[X],
            y=df[Y],
            customdata=df[KEY],
            mode="markers",
            marker=dict(size=4, color=SELECTED_COLOR),
            selected=dict(marker=dict(color=SELECTED_COLOR)),
            unselected=dict(marker=dict(color=UNSELECTED_COLOR, opacity=UNSELECTED_OPACITY)),
            hovertemplate="%{customdata}<br>%{x} MW<br>%{y} GWh<extra></extra>",
        ))
        fig.update_layout(
            dragmode="select",
            margin=dict(l=50, r=10, t=10, b=40),
            xaxis=dict(title=X, type="log"),
            yaxis=dict(title=Y, type="log"),
        )
        return fig


def make_scatterplot(df):
    # Log axes cannot show zero or missing values, so those plants are left out here.
    shown = df[(df[X] > 0) & (df[Y] > 0)]
    return Scatterplot("Placeholder scatterplot", shown)
