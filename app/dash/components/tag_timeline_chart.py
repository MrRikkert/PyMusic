from datetime import datetime

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from app.dash.app import app
from app.dash.utils import (
    add_date_clause,
    convert_dates,
    get_agg,
    get_default_graph,
    seconds_to_text,
)
from app.db.base import db
from dash.dependencies import Input, Output, State
from dateutil.relativedelta import relativedelta
from pony.orm import db_session


def get_layout():
    return (
        dbc.Card(
            dbc.CardBody(get_default_graph(id="tag-timeline")),
            color="light",
            outline=True,
            className="tag-timeline",
        ),
    )


@app.callback(
    Output("tag-timeline", "figure"),
    Input("date-select", "value"),
    Input("use-playtime", "value"),
    State("date-range-select", "value"),
)
@convert_dates
@db_session
def _plays_bar_chart(min_date, playtime, date_range, max_date):
    if date_range == "week":
        min_date = min_date - relativedelta(weeks=11)
        resample = "W-MON"
        frmt = "%W, %Y"
        group = 'EXTRACT(week FROM sc.date), EXTRACT("year" FROM sc.date)'
        title = "Tag timeline (last 12 weeks)"
    elif date_range == "month":
        min_date = min_date - relativedelta(months=11)
        resample = "MS"
        frmt = "%b, %Y"
        group = 'EXTRACT(month FROM sc.date), EXTRACT("year" FROM sc.date)'
        title = "Tag timeline (last 12 months)"
    elif date_range == "year":
        resample = "MS"
        frmt = "%b"
        group = 'EXTRACT(month FROM sc.date), EXTRACT("year" FROM sc.date)'
        title = "Tag timeline (year)"

    sql = f"""
    SELECT *
    FROM (
        SELECT
            MIN(sc.date) as "date",
            t.value,
            {get_agg(playtime)}(s.length) AS "time",
            dense_rank() over (
                partition by
                    {group}
                order by
                    {get_agg(playtime)}(s.length) desc
                ) as rank
        FROM scrobble sc
        INNER JOIN song s
            ON sc.song = s.id
        INNER JOIN songdb_tagdb s_t
            ON s_t.songdb = s.id
        INNER JOIN tag t
            ON s_t.tagdb = t.id
        WHERE t.tag_type = 'type'
            :date:
        GROUP BY {group}, t.value
    ) sub
    WHERE rank <= 5
    ORDER BY "date", rank, "time"
    """
    sql = add_date_clause(sql, min_date, max_date, where=False)

    df = pd.read_sql_query(
        sql,
        db.get_connection(),
        params={"min_date": min_date, "max_date": max_date},
        parse_dates=["date"],
    )
    df = (
        df.groupby("value")
        .apply(
            lambda x: x.drop_duplicates("date")
            .set_index("date")
            .resample(resample)
            .agg({"rank": "min", "time": "min"})
        )
        .reset_index()
    )
    df = df.loc[df.date < max_date]
    df["x"] = df.date.dt.strftime(frmt)
    df["rank"] = df["rank"].replace(0, np.NaN)
    if playtime:
        df["time"] = df["time"].apply(lambda x: seconds_to_text(x))

    fig = px.line(
        df,
        x="x",
        y="rank",
        color="value",
        custom_data=["value", "time"],
        color_discrete_sequence=px.colors.qualitative.G10,
        title=title,
    )

    fig.update_layout(
        hovermode="x",
        yaxis=dict(range=[5.5, 0.5], fixedrange=True),
        xaxis=dict(fixedrange=True),
        showlegend=False,
    )

    fig.update_traces(
        hovertemplate="<br>".join(
            [
                "Tag: %{customdata[0]} <extra></extra>",
                "Playtime: %{customdata[1]}" if playtime else "Plays: %{customdata[1]}",
            ]
        ),
        line=dict(shape="spline", smoothing=1),
        marker=dict(size=12),
        connectgaps=False,
        mode="markers+lines",
    )

    for i, d in enumerate(fig.data):
        idx = pd.Series(d.y).last_valid_index()
        if not idx:
            continue
        fig.add_scatter(
            x=[d.x[idx]],
            y=[d.y[idx]],
            mode="markers+text",
            text=d.customdata[idx],
            textfont=dict(color=d.line.color),
            textposition="top center",
            marker=dict(color=d.line.color, size=12),
            showlegend=False,
            hoverinfo="skip",
        )

    return fig
