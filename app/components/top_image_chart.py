import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, html
from pony.orm import db_session

from app.app import app
from app.utils import get_art_url, seconds_to_text


def get_layout(_type):
    title_style = {
        "position": "absolute",
        "padding": "5px 10px",
        "border-radius": "10px",
        "margin": "5px",
        "background-color": "rgba(255,255,255,0.4)",
        "color": "black",
        "font-weight": "bold",
        "z-index": "1",
    }
    playtime_style = title_style.copy()
    playtime_style["right"] = "0px"
    artist_style = {"font-size": "1rem", "color": "#111", "font-weight": "400"}
    name_style = {
        "position": "absolute",
        "bottom": "0px",
        "padding": "5px 10px",
        "font-size": "1.1rem",
        "font-weight": "bold",
        "background-color": "rgba(255,255,255,0.4)",
        "color": "black",
        "width": "100%",
    }

    def get_card(title, id, artist=False, className=""):
        return (
            dbc.Card(
                [
                    html.Div(title, style=title_style),
                    html.Div(
                        "Loading...", style=playtime_style, id=id + "-top-playtime"
                    ),
                    html.Div(
                        [
                            html.Div(
                                dbc.CardImg(
                                    src="/assets/img/placeholder_album_art.png",
                                    id=id + "-top-image",
                                    top=True,
                                    style={
                                        "object-fit": "cover",
                                        "position": "absolute",
                                        "top": "0",
                                        "left": "0",
                                        "bottom": "0",
                                        "right": "0",
                                        "height": "100%",
                                    },
                                    class_name="img-fluid",
                                ),
                                className="top-chart-image-top-image-box",
                            ),
                            html.Div(
                                [
                                    html.Div("Loading...", id=id + "-top-name"),
                                    html.Div(
                                        "Loading...",
                                        id=id + "-top-artist",
                                        style=artist_style,
                                    )
                                    if artist
                                    else None,
                                ],
                                style=name_style,
                            ),
                        ],
                        style={"position": "relative"},
                    ),
                    dbc.CardBody([], id=id),
                ],
                color="light",
                outline=True,
            ),
        )

    artist = False
    if _type == "mixed":
        _id = "top-mixed-image-chart"
        title = "Top tag"
    elif _type == "artist":
        _id = "top-artist-image-chart"
        title = "Top artist"
    elif _type == "album":
        _id = "top-album-image-chart"
        title = "Top album"
        artist = True

    return get_card(title, _id, artist=artist)


def _get_rows(df, name_column):
    rows = []
    for idx, row in df.iterrows():
        background = f"linear-gradient(90deg, #0567a4 {row['relative']}%, rgba(0,0,0,0) {row['relative']}%)"  # noqa
        rows.append(
            html.Div(
                [
                    html.Div(
                        idx + 1,
                        style={"padding-right": "5px", "margin-left": "10px"},
                        className="fw-bold",
                    ),
                    html.Img(
                        src=row["Art"],
                        className="me-3",
                        style={"width": "60px", "height": "60px", "padding": "5px"},
                    ),
                    html.Div(
                        [
                            html.Div(
                                row[name_column],
                                className="text-white",
                                style={
                                    "white-space": "nowrap",
                                    "overflow": "hidden",
                                    "text-overflow": "ellipsis",
                                },
                            ),
                            html.Div(row["seconds"], className="text-muted"),
                        ],
                        style={"flex": "1", "min-width": "0"},
                    ),
                ],
                className="d-flex align-items-center",
                style={"background": background, "margin-top": "5px"},
            )
        )

    return rows


def __get_data(df, playtime):
    df = pd.read_json(df, orient="split")
    df["relative"] = df["seconds"] / df.iloc[0]["seconds"] * 100
    if playtime:
        df["seconds"] = df["seconds"].apply(seconds_to_text)
    else:
        df["seconds"] = df["seconds"].apply(lambda i: f"{i} plays")

    df.loc[df.index[0], "Art"] = get_art_url(df.iloc[0]["Art"], size=512)
    df.loc[df.index[1:], "Art"] = df.loc[df.index[1:], "Art"].apply(
        get_art_url, size=64
    )
    return df


@app.callback(
    Output("top-mixed-image-chart-top-name", "children"),
    Output("top-mixed-image-chart-top-playtime", "children"),
    Output("top-mixed-image-chart-top-image", "src"),
    Output("top-mixed-image-chart", "children"),
    Input("top-tags", "data"),
    State("use-playtime", "value"),
)
@db_session
def _top_mixed(df, playtime):
    df = __get_data(df, playtime)
    return (
        df.iloc[0]["Name"],
        df.iloc[0]["seconds"],
        df.iloc[0]["Art"],
        _get_rows(df.iloc[1:], "Name"),
    )


@app.callback(
    Output("top-artist-image-chart-top-name", "children"),
    Output("top-artist-image-chart-top-playtime", "children"),
    Output("top-artist-image-chart-top-image", "src"),
    Output("top-artist-image-chart", "children"),
    Input("top-artists", "data"),
    State("use-playtime", "value"),
)
@db_session
def _top_artists(df, playtime):
    df = __get_data(df, playtime)
    return (
        df.iloc[0]["Artist"],
        df.iloc[0]["seconds"],
        df.iloc[0]["Art"],
        _get_rows(df.iloc[1:], "Artist"),
    )


@app.callback(
    Output("top-album-image-chart-top-name", "children"),
    Output("top-album-image-chart-top-playtime", "children"),
    Output("top-album-image-chart-top-artist", "children"),
    Output("top-album-image-chart-top-image", "src"),
    Output("top-album-image-chart", "children"),
    Input("top-albums", "data"),
    State("use-playtime", "value"),
)
@db_session
def _top_albums(df, playtime):
    df = __get_data(df, playtime)
    return (
        df.iloc[0]["Album"],
        df.iloc[0]["seconds"],
        df.iloc[0]["Artist"],
        df.iloc[0]["Art"],
        _get_rows(df.iloc[1:], "Album"),
    )
