import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Input, Output, State
from dateutil.relativedelta import relativedelta
from pony.orm import db_session

from app.app import app
from app.utils import (
    get_agg,
    get_default_graph,
    get_df_from_sql,
    get_min_max_date,
    seconds_to_text,
)


def get_layout():
    return (
        dbc.Card(
            dbc.CardBody(get_default_graph(id="tag-timeline")),
            color="light",
            outline=True,
            class_name="n6",
        ),
    )


def _get_vars(date_range, min_date):
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
    return min_date, resample, frmt, group, title


def _get_data(playtime, min_date, max_date, group, resample, frmt):
    sql = f"""
        SELECT
            MIN(sc.date) as "date",
            t.value,
            {get_agg(playtime)}(s.length) AS "time"
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
    """
    df = get_df_from_sql(sql, min_date, max_date, where=False)

    # Fill missing dates with NaNs
    # make lines disconnect when a group dissapears for a time frame
    df = (
        df.groupby("value")
        .apply(
            lambda x: x.drop_duplicates("date")
            .set_index("date")
            .resample(resample)
            .sum()
        )
        .reset_index()
    )
    df["time"] = df["time"].replace(0, np.NaN)
    df = df.loc[df.date < pd.to_datetime(max_date)]
    df["rank"] = df.groupby(pd.Grouper(key="date", freq=resample))["time"].rank(
        ascending=False, method="first"
    )
    df["x"] = df.date.dt.strftime(frmt)

    if playtime:
        df["time"] = df["time"].apply(lambda x: seconds_to_text(x))

    df.loc[df["rank"] > 5, "rank"] = np.NaN
    return df.sort_values("date")


def _add_scatter(fig):
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


@app.callback(
    Output("tag-timeline", "figure"),
    Input("date-select", "value"),
    Input("use-playtime", "value"),
)
@db_session
def _plays_bar_chart(min_date, playtime):
    min_date, max_date, date_range = get_min_max_date(min_date)
    min_date, resample, frmt, group, title = _get_vars(date_range, min_date)
    df = _get_data(playtime, min_date, max_date, group, resample, frmt)

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

    fig = _add_scatter(fig)
    return fig
