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


def add_date_clause(sql: str, min_date: datetime, max_date: datetime) -> str:
    if min_date and max_date:
        return sql.replace(
            ":date:", "AND sc.date > %(min_date)s AND sc.date <= %(max_date)s"
        )
    return sql.replace(":date:", "")


def set_theme(fig):
    fig.update_layout(
        margin=dict(l=10, r=10, b=10, t=40),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        template="plotly_dark",
    )
