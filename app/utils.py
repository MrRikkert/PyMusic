from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def get_min_max_date(min_date, date_range):
    min_date = datetime.strptime(min_date, "%Y-%m-%d")
    if date_range == "week":
        max_date = min_date + timedelta(days=7)
    elif date_range == "month":
        max_date = min_date + relativedelta(months=1)
    elif date_range == "year":
        max_date = min_date + relativedelta(years=1)
    return min_date, max_date
