import altair as alt
import dash_alternative_viz as dav
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output
from pony.orm import db_session

from app.app import app
from app.utils import get_agg, get_df_from_sql

colors = [
    "#838B8B",
    "#7A8B8B",
    "#C1CDCD",
    "#668B8B",
    "#B4CDCD",
    "#2F4F4F",
    "#2F4F4F",
    "#5F9F9F",
    "#C0D9D9",
    "#528B8B",
    "#E0EEEE",
    "#96CDCD",
    "#388E8E",
    "#79CDCD",
    "#D1EEEE",
    "#8FD8D8",
    "#66CCCC",
    "#ADEAEA",
    "#70DBDB",
    "#AEEEEE",
    "#AFEEEE",
    "#8DEEEE",
    "#37FDFC",
    "#008080",
    "#008B8B",
    "#00CDCD",
    "#00EEEE",
    "#00FFFF",
    "#00FFFF",
    "#97FFFF",
    "#BBFFFF",
    "#E0FFFF",
    "#F0FFFF",
    "#00CED1",
    "#5F9EA0",
    "#00868B",
    "#00C5CD",
    "#00E5EE",
    "#00F5FF",
    "#67E6EC",
    "#4A777A",
    "#05EDFF",
    "#53868B",
    "#73B1B7",
    "#05E9FF",
    "#7AC5CD",
    "#8EE5EE",
    "#05B8CC",
    "#98F5FF",
    "#B0E0E6",
    "#C1F0F6",
    "#39B7CD",
    "#65909A",
    "#0EBFE9",
    "#C3E4ED",
    "#68838B",
    "#63D1F4",
    "#9AC0CD",
    "#50A6C2",
    "#ADD8E6",
    "#B2DFEE",
    "#00688B",
    "#0099CC",
    "#009ACD",
    "#00B2EE",
    "#00BFFF",
    "#BFEFFF",
    "#33A1C9",
    "#507786",
    "#87CEEB",
    "#38B0DE",
    "#0BB5FF",
    "#42C0FB",
    "#6996AD",
    "#539DC2",
    "#236B8E",
    "#3299CC",
    "#0198E1",
    "#33A1DE",
    "#607B8B",
    "#35586C",
    "#5D92B1",
    "#8DB6CD",
    "#325C74",
    "#A4D3EE",
    "#82CFFD",
    "#67C8FF",
    "#B0E2FF",
    "#87CEFA",
    "#6CA6CD",
    "#4A708B",
    "#9BC4E2",
    "#7EC0EE",
    "#87CEFF",
    "#517693",
    "#5D7B93",
    "#42647F",
    "#4682B4",
    "#4F94CD",
    "#5CACEE",
    "#63B8FF",
    "#525C65",
    "#36648B",
    "#62B1F6",
    "#74BBFB",
    "#F0F8FF",
    "#4E78A0",
    "#0D4F8B",
    "#708090",
    "#708090",
    "#778899",
    "#778899",
    "#6183A6",
    "#9FB6CD",
    "#7D9EC0",
    "#104E8B",
    "#1874CD",
    "#1C86EE",
    "#60AFFE",
    "#007FFF",
    "#1E90FF",
    "#6C7B8B",
    "#B7C3D0",
    "#739AC5",
    "#75A1D0",
    "#B9D3EE",
    "#499DF5",
    "#C6E2FF",
    "#3B6AA0",
    "#7AA9DD",
    "#0276FD",
    "#003F87",
    "#6E7B8B",
    "#506987",
    "#A2B5CD",
    "#4372AA",
    "#26466D",
    "#1D7CF2",
    "#687C97",
    "#344152",
    "#50729F",
    "#4973AB",
    "#B0C4DE",
    "#3063A5",
    "#BCD2EE",
    "#7EB6FF",
    "#CAE1FF",
    "#4D71A3",
    "#2B4F81",
    "#4981CE",
    "#88ACE0",
    "#5993E5",
    "#3A66A7",
    "#3579DC",
    "#5190ED",
    "#42526C",
    "#4D6FAC",
    "#2C5197",
    "#6495ED",
    "#6D9BF1",
    "#5B90F6",
    "#1464F4",
    "#3A5894",
    "#7093DB",
    "#1B3F8B",
    "#5971AD",
    "#0147FA",
    "#3D59AB",
    "#27408B",
    "#3A5FCD",
    "#4169E1",
    "#436EEE",
    "#003EFF",
    "#4876FF",
    "#A9ACB6",
    "#22316C",
    "#162252",
    "#3B4990",
    "#283A90",
    "#6F7285",
    "#838EDE",
    "#E6E8FA",
    "#7D7F94",
    "#2E37FE",
    "#2F2F4F",
    "#42426F",
    "#8F8FBC",
    "#5959AB",
    "#7171C6",
    "#D9D9F3",
    "#23238E",
    "#3232CC",
    "#3232CD",
    "#191970",
    "#E6E6FA",
    "#000033",
    "#000080",
    "#00008B",
    "#00009C",
    "#0000CD",
    "#0000EE",
    "#0000FF",
    "#3333FF",
    "#4D4DFF",
    "#6666FF",
    "#AAAAFF",
    "#CCCCFF",
    "#F8F8FF",
    "#5B59BA",
    "#120A8F",
    "#302B54",
    "#483D8B",
    "#473C8B",
    "#3B3178",
    "#6A5ACD",
    "#6959CD",
    "#7A67EE",
    "#8470FF",
    "#836FFF",
    "#7B68EE",
    "#3300FF",
    "#5D478B",
    "#9F79EE",
    "#8968CD",
    "#9370DB",
    "#AB82FF",
    "#6600FF",
    "#380474",
]


def get_layout():
    def get_card():
        return (
            dbc.Card(
                dbc.CardBody(dav.VegaLite(id="streamgraph")),
                color="light",
                outline=True,
                style={"overflow": "auto"},
            ),
        )

    return get_card()


@app.callback(Output("streamgraph", "spec"), Input("use-playtime", "value"))
@db_session
def _get_streamgraph(playtime):
    sql = f"""
    SELECT
        "date",
        "tag_type",
        "name" AS "album",
        "plays" AS "length"
    FROM (
        SELECT
            "date",
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
            {get_agg(playtime)}(agg) plays
        FROM (
            SELECT
                date_trunc('month', sc.date) as "date",
                MIN(s.length) AS agg,
                MIN(franchise.value) AS franchise,
                MIN(sort_artist.value) AS sort_artist,
                MIN("type".value) AS "type"
            FROM scrobble sc
            INNER JOIN song s
                ON s.id = sc.song
            INNER JOIN songdb_tagdb st
                ON s.id = st.songdb
            LEFT JOIN tag franchise
                ON franchise.id = st.tagdb AND franchise.tag_type = 'franchise'
            LEFT JOIN tag sort_artist
                ON sort_artist.id = st.tagdb AND sort_artist.tag_type = 'sort_artist'
            LEFT JOIN tag "type"
                ON "type".id = st.tagdb AND "type".tag_type = 'type'
            GROUP BY "date", sc.id
        ) x
        GROUP BY "date", tag_type, "name", "type"
        ORDER BY "date", "plays" DESC
    ) y
    """
    df = get_df_from_sql(sql, None, None, where=False, parse_dates="date")
    # df = pd.read_sql_query(sql, db.get_connection(), parse_dates="date")
    df.index = df["date"]

    df = df.groupby("album").resample("D").mean().reset_index()

    d = df.set_index(["date", "album"])
    midx = pd.MultiIndex.from_product(
        [pd.date_range(df["date"].min(), df["date"].max()), df["album"].unique()],
        names=d.index.names,
    )
    df = d.reindex(midx, fill_value=0).reset_index()

    dfs = []
    for album in df["album"].unique():
        try:
            _df = df.loc[df["album"] == album].copy()
            _df2 = _df.copy()
            _df["length"] = _df["length"].interpolate(method="linear")
            _df.index = _df["date"]
            _df["length"] = _df["length"].clip(0, _df2["length"].max())
            _df["length"] = (
                _df["length"]
                .rolling(
                    window=45,
                    win_type="gaussian",
                    closed="neither",
                    center=True,
                    min_periods=1,
                )
                .mean(std=20)
            )
            dfs.append(_df)
        except Exception as e:
            print(e)

    df = pd.concat(dfs).reset_index(drop=True)

    alt.data_transformers.disable_max_rows()
    alt.renderers.set_embed_options(theme="dark")
    return (
        alt.Chart(df)
        .mark_area()
        .encode(
            alt.X("date:T", axis=alt.Axis(format="%b, %Y", domain=False, tickSize=0)),
            alt.Y("length:Q", stack="center", axis=None),
            alt.Color("album:N", legend=None),
            tooltip=["album", "date"],
        )
        .configure_range(category={"scheme": colors})
        .properties(width=3000, height=500)
        .to_dict()
    )
