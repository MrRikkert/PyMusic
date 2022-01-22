import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, State
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
            dbc.CardBody(get_default_graph(id="vocal-dist-chart")),
            color="light",
            outline=True,
            className="vocal-chart",
            style={"height": "110px"},
        ),
    )


@app.callback(
    Output("vocal-dist-chart", "figure"),
    Input("use-playtime", "value"),
    Input("date-select", "value"),
    State("date-range-select", "value"),
)
@db_session
def _vocal_chart(playtime, min_date, date_range):
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
    WHERE t.tag_type = 'vocals'
        :date:
    GROUP BY t.value
    """
    min_date, max_date = get_min_max_date(min_date, date_range)
    df = get_df_from_sql(sql, min_date, max_date, where=False)

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
