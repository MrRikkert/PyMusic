import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from app.dash.app import app
from app.dash.utils import get_default_graph
from dash.dependencies import Input, Output, State


def get_layout(_type, reverse=False):
    def get_card(id, className=""):
        return (
            dbc.Card(
                dbc.CardBody(get_default_graph(id=id, className=className)),
                color="light",
                outline=True,
                className="top-chart",
            ),
        )

    if _type == "mixed":
        _id = "top-mixed-chart"
    elif _type == "artist":
        _id = "top-artist-chart"
    elif _type == "album":
        _id = "top-album-chart"

    if reverse:
        return get_card(_id, "reversed")
    return get_card(_id)


def _get_graph(df, x, y, title, xaxis_title, className=""):
    fig = px.bar(
        df, x=x, y=y, orientation="h", title=title, hover_data=["Time"], text=y
    )
    fig.update_layout(
        xaxis=dict(title=xaxis_title), uniformtext=dict(minsize=13, mode="show")
    )
    fig.update_traces(textposition="inside", insidetextanchor="start", textangle=0)
    fig.update_yaxes(showticklabels=False)
    if "reversed" in className:
        fig.update_xaxes(autorange="reversed")

    return fig


@app.callback(
    Output("top-mixed-chart", "figure"),
    Input("top-tags", "data"),
    State("top-tags-scale", "data"),
    State("top-mixed-chart", "className"),
    State("use-playtime", "value"),
)
def _top_tag(df, scale, className, playtime):
    df = pd.read_json(df, orient="split")
    if playtime:
        title = "Top tag (playtime)"
        xaxis_title = f"Total Playtime ({scale})"
    else:
        title = "Top tag (plays)"
        xaxis_title = f"Total Plays"

    return _get_graph(
        df=df,
        x="Time",
        y="Name",
        title=title,
        xaxis_title=xaxis_title,
        className=className,
    )


@app.callback(
    Output("top-artist-chart", "figure"),
    Input("top-artists", "data"),
    State("top-artists-scale", "data"),
    State("top-artist-chart", "className"),
    State("use-playtime", "value"),
)
def _top_artist(df, scale, className, playtime):
    df = pd.read_json(df, orient="split")
    if playtime:
        title = "Top artist (playtime)"
        xaxis_title = f"Total Playtime ({scale})"
    else:
        title = "Top artist (plays)"
        xaxis_title = f"Total Plays"

    return _get_graph(
        df=df,
        x="Time",
        y="Artist",
        title=title,
        xaxis_title=xaxis_title,
        className=className,
    )


@app.callback(
    Output("top-album-chart", "figure"),
    Input("top-albums", "data"),
    State("top-albums-scale", "data"),
    State("top-album-chart", "className"),
    State("use-playtime", "value"),
)
def _top_album(df, scale, className, playtime):
    df = pd.read_json(df, orient="split")

    if playtime:
        title = "Top albums (Playtime)"
        xaxis_title = f"Total Playtime ({scale})"
    else:
        title = "Top albums (plays)"
        xaxis_title = f"Total Plays"

    return _get_graph(
        df=df,
        x="Time",
        y="Album",
        title=title,
        xaxis_title=xaxis_title,
        className=className,
    )
