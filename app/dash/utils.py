from datetime import datetime
from inspect import getfullargspec


def convert_dates(func):
    argspec = getfullargspec(func)
    min_date = argspec.args.index("min_date")
    max_date = argspec.args.index("max_date")

    def wrap(*args, **kwargs):
        args = list(args)
        if args[min_date]:
            args[min_date] = datetime.strptime(args[min_date], "%Y-%m-%d")
        if args[max_date]:
            args[max_date] = datetime.strptime(args[max_date], "%Y-%m-%d")
        return func(*args, **kwargs)

    return wrap


def set_theme(func):
    def wrap(*args, **kwargs):
        fig = func(*args, **kwargs)
        fig.update_layout(
            margin=dict(l=10, r=10, b=10, t=40),
            plot_bgcolor="rgba(0, 0, 0, 0)",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            template="plotly_dark",
        )
        return fig

    return wrap


def add_date_clause(
    sql: str, min_date: datetime, max_date: datetime, where=True
) -> str:
    if min_date and max_date:
        condition = "sc.date > %(min_date)s AND sc.date <= %(max_date)s"
        if where:
            condition = "WHERE " + condition
        else:
            condition = "AND " + condition
        return sql.replace(":date:", condition)
    return sql.replace(":date:", "")


def set_length_scale(df, column):
    if df.iloc[-1][column] > 172_800:
        df[column] = df[column] / (24 * 60 * 60)
        scale = "days"
    elif df.iloc[-1][column] > 7200:
        df[column] = df[column] / (60 * 60)
        scale = "hours"
    elif df.iloc[-1][column] > 120:
        df[column] = df[column] / 60
        scale = "minutes"
    else:
        scale = "seconds"
    return (df, scale)
