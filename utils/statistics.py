from datetime import date,  datetime, timedelta, timezone


def fill_missing_dates(data, event_type, days=28):
    today = date.today()
    start_day = today - timedelta(days=days-1)
    date_range = [start_day + timedelta(days=i) for i in range(days)]

    data_dict = {d["day"].isoformat(): d[event_type] for d in data}

    filled = [
        {"day": d.strftime("%m-%d"),
         event_type: data_dict.get(d.isoformat(), 0)}
        for d in date_range
    ]
    total = sum(item[event_type] for item in filled)
    return filled, total


def get_percent(data, event_type):
    total = sum(x[event_type] for x in data)
    for x in data:
        x["percent"] = int(round(x[event_type] * 100 / total)) if total else 0
    return data
