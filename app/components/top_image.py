import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, html
from pony.orm import db_session

from app.app import app
from app.utils import get_agg, get_df_from_sql, get_min_max_date
from shared.settings import IMG_URL


def get_layout(_type):
    title_style = {
        "position": "absolute",
        "padding": "5px 10px",
        "border-radius": "10px",
        "margin": "5px",
        "background-color": "rgba(255,255,255,0.4)",
        "color": "black",
        "font-weight": "bold",
    }
    img_style = {"object-fit": "cover"}
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

    def get_card(title, name_id, art_id, artist_id=None):
        return dbc.Card(
            [
                html.Div(title, className="title", style=title_style),
                dbc.CardImg(
                    src="/assets/img/placeholder_album_art.png",
                    id=art_id,
                    top=True,
                    style=img_style,
                ),
                html.Div(
                    [
                        html.Div(id=name_id),
                        html.Div(id=artist_id, className="artist", style=artist_style)
                        if artist_id
                        else None,
                    ],
                    className="name",
                    style=name_style,
                ),
            ],
            color="light",
            outline=True,
            className="top-image",
            style={"height": "auto"},
        )

    if _type == "mixed":
        name_id = "top-mixed-image-name"
        art_id = "top-mixed-image-art"
        return get_card("Top tag", name_id, art_id)
    elif _type == "album":
        name_id = "top-album-image-name"
        art_id = "top-album-image-art"
        artist_id = "top-album-image-artist"
        return get_card("Top album", name_id, art_id, artist_id)
    elif _type == "artist":
        name_id = "top-artist-image-name"
        art_id = "top-artist-image-art"
        return get_card("Top artist", name_id, art_id)


@app.callback(
    Output("top-mixed-image-name", "children"),
    Output("top-mixed-image-art", "src"),
    Input("top-tags", "data"),
    State("date-range-select", "value"),
    State("date-select", "value"),
    State("use-playtime", "value"),
)
@db_session
def _top_image_mixed_stats(df, date_range, min_date, playtime):
    min_date, max_date = get_min_max_date(min_date, date_range)
    df = pd.read_json(df, orient="split")

    sql = f"""
    SELECT art
    FROM album a
    INNER JOIN albumdb_songdb a_s
        ON a_s.albumdb = a.id
    INNER JOIN song s
        ON a_s.songdb = s.id
    INNER JOIN scrobble sc
        ON sc.song = s.id
    INNER JOIN songdb_tagdb s_t
        ON s_t.songdb = s.id
    INNER JOIN tag t
        ON s_t.tagdb = t.id
    WHERE t.value = '{df.iloc[-1]["Name"]}'
        :date:
    GROUP BY art
    ORDER BY {get_agg(playtime)}(s.length) DESC
    LIMIT 1
    """
    df_art = get_df_from_sql(sql, min_date, max_date, where=False).iloc[0]
    art = IMG_URL + df_art.art

    return (df.iloc[-1]["Name"], art)


@app.callback(
    Output("top-artist-image-name", "children"),
    Output("top-artist-image-art", "src"),
    Input("top-artists", "data"),
)
def _top_image_artist_stats(df):
    df = pd.read_json(df, orient="split")

    top = df.iloc[-1]
    art = IMG_URL + top.Art
    return (top.Artist, art)
