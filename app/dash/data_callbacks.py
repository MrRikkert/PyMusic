import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from pony.orm import db_session

from app.dash.app import app
from app.dash.utils import add_date_clause, convert_dates, get_agg, set_length_scale
from app.db.base import db
from dash.dependencies import Input, Output


def get_layout():
    return html.Div([dcc.Store("top-tags"), dcc.Store("top-tags-scale")])


@app.callback(
    Output("top-tags", "data"),
    Output("top-tags-scale", "data"),
    Input("date-range-select", "value"),
    Input("date-select", "value"),
    Input("top-mixed-chart", "className"),
    Input("use-playtime", "checked"),
)
@convert_dates
@db_session
def _top_tags(date_range, min_date, className, playtime, max_date):
    sql = f"""
    SELECT
        CASE
            WHEN franchise IS NOT NULL THEN 'franchise'
            WHEN sort_artist IS NOT NULL THEN 'sort_artist'
            WHEN "type" IS NOT NULL THEN 'type'
        END AS "tag_type",
        CASE
            WHEN franchise IS NOT NULL THEN franchise
            WHEN sort_artist IS NOT NULL THEN sort_artist
            WHEN "type" IS NOT NULL THEN "type"
        END AS "name",
        {get_agg(playtime)}("length") AS plays
    FROM (
        SELECT
            sc.id,
            s.length,
            MAX(CASE WHEN t.tag_type = 'franchise' THEN t.value END) AS "franchise",
            MAX(CASE WHEN t.tag_type = 'sort_artist' THEN t.value END) AS "sort_artist",
            MAX(CASE WHEN t.tag_type = 'type' THEN t.value END) AS "type"
        FROM scrobble sc
        INNER JOIN song s
            ON s.id = sc.song
        INNER JOIN songdb_tagdb st
            ON s.id = st.songdb
        INNER JOIN tag t
            ON t.id = st.tagdb
        :date:
        GROUP BY sc.id, s.length
    ) x
    GROUP BY "name", "tag_type"
    ORDER BY plays DESC
    LIMIT 5
    """
    sql = add_date_clause(sql, min_date, max_date, where=True)

    df = pd.read_sql_query(
        sql, db.get_connection(), params={"min_date": min_date, "max_date": max_date}
    )
    df = df.rename(
        columns={df.columns[0]: "Type", df.columns[1]: "Name", df.columns[2]: "Time"}
    )
    df = df.sort_values("Time", ascending=True)
    df, scale = set_length_scale(df, "Time", playtime)
    return df.to_json(date_format="iso", orient="split"), scale
