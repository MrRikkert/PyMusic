import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output
from pony.orm import db_session

from app.app import app
from app.utils import (
    get_agg,
    get_default_graph,
    get_df_from_sql,
    get_min_max_date,
    set_length_scale,
)


def get_layout():
    return (
        dbc.Card(
            dbc.CardBody(get_default_graph(id="listening-clock")),
            color="light",
            outline=True,
            className="listening-clock",
            style={"height": "300px"},
        ),
    )


@app.callback(
    Output("listening-clock", "figure"),
    Input("date-range-select", "value"),
    Input("date-select", "value"),
    Input("use-playtime", "value"),
)
@db_session
def _listening_clock(date_range, min_date, playtime):
    sql = f"""
    SELECT
        EXTRACT(HOUR FROM DATE) AS "hour",
        {get_agg(playtime)}(s.length) AS "time"
    FROM scrobble sc
    INNER JOIN song s
        ON sc.song = s.id
    :date:
    GROUP BY "hour"
    """
    min_date, max_date = get_min_max_date(min_date, date_range)
    df = get_df_from_sql(sql, min_date, max_date)
    df["hour"] = df.hour * 15
    df, scale = set_length_scale(df, "time", playtime)

    if playtime:
        title = "Listening clock (Playtime)"
    else:
        title = "Listening clock (plays)"

    fig = px.bar_polar(df, r="time", theta="hour", labels="time", title=title)

    fig.update_polars(
        angularaxis=dict(
            direction="clockwise",
            tickvals=[hr * 15 for hr in range(24)],
            ticktext=[f"{hr}h" for hr in range(24)],
        ),
        radialaxis=dict(visible=False),
        hole=0.2,
    )
    fig.update_layout(margin=dict(l=10, r=10, b=20, t=50))

    return fig
