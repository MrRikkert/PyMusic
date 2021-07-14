import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from app.dash.app import app
from app.dash.utils import (
    add_date_clause,
    convert_dates,
    get_agg,
    get_default_graph,
    set_length_scale,
)
from app.db.base import db
from dash.dependencies import Input, Output, State
from pony.orm import db_session


def get_layout():
    return (
        dbc.Card(
            dbc.CardBody(get_default_graph(id="vocal-dist-chart")),
            color="light",
            outline=True,
            className="height-2",
        ),
    )


def _get_graph(df, x, y, title, xaxis_title, className=""):
    fig = px.bar(
        df, x=x, y=y, orientation="h", title=title, hover_data=["Time"], text=y
    )
    fig.update_layout(
        xaxis_title=xaxis_title, uniformtext_minsize=13, uniformtext_mode="show"
    )
    fig.update_traces(textposition="inside", insidetextanchor="start", textangle=0)
    fig.update_yaxes(showticklabels=False)
    if "reversed" in className:
        fig.update_xaxes(autorange="reversed")

    return fig


@app.callback(
    Output("vocal-dist-chart", "figure"),
    Input("use-playtime", "value"),
    Input("date-select", "value"),
    State("date-range-select", "value"),
)
@convert_dates
@db_session
def _top_tag(playtime, min_date, date_range, max_date):
    sql = f"""
    SELECT
        t.value,
        {get_agg(playtime)}(s.length) AS time
    FROM scrobble sc
    INNER JOIN song s
        ON sc.song = s.id
    INNER JOIN songdb_tagdb s_t
        ON s_t.songdb = s.id
    INNER JOIN tag t
        ON s_t.tagdb = t.id
    WHERE t.tag_type = 'vocals?'
        :date:
    GROUP BY t.value
    """
    sql = add_date_clause(sql, min_date, max_date, where=False)
    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )
    df, scale = set_length_scale(df, "time", playtime)
    df["percent"] = df.time / df.time.sum() * 100
    df["group"] = "group"
    df["scale"] = scale

    fig = px.bar(
        df,
        x="percent",
        y="group",
        color="value",
        orientation="h",
        barmode="stack",
        title="Vocals/Instrumental distribution",
        text=df.apply(lambda row: f"{row.value} - {row.percent:.1f}%", axis=1),
        custom_data=["value", df.time, df.scale],
    )

    fig.update_layout(
        xaxis=dict(visible=False, range=[0, 100], fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        uniformtext=dict(minsize=13, mode="show"),
        showlegend=False,
    )

    fig.update_traces(
        insidetextanchor="middle",
        hovertemplate="<br>".join(
            [
                "Value: %{customdata[0]}",
                "Percent: %{x:.1f}%",
                "Time: %{customdata[1]:.1f} %{customdata[2]}"
                if playtime
                else "Scrobbles: %{customdata[1]:.0f}",
                "<extra></extra>",
            ]
        ),
    )

    return fig
