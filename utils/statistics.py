from datetime import date,  datetime, timedelta, timezone


def fill_missing_dates(data, days=28):
    today = date.today()
    start_day = today - timedelta(days=days-1)
    date_range = [start_day + timedelta(days=i) for i in range(days)]

    data_dict = {d["day"].isoformat(): d["clickCount"] for d in data}

    filled = [
        {"day": d.strftime("%m-%d"),
         "clickCount": data_dict.get(d.isoformat(), 0)}
        for d in date_range
    ]

    return filled


def get_percent(data):
    total = sum(x["clicks"] for x in data)
    for x in data:
        x["percent"] = int(round(x["clicks"] * 100 / total)) if total else 0
    return data
