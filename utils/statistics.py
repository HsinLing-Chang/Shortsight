from datetime import date,  datetime, timedelta, timezone


def fill_missing_dates(data, days=28):
    today = date.today()  # 取得今天的日期
    start_day = today - timedelta(days=days-1)  # 算出「30 天前」是哪一天
    date_range = [start_day + timedelta(days=i) for i in range(days)]
    # 建立一個日期範圍列表，從 start_day 連續加一天，總共 days（預設 30 天）

    data_dict = {d["day"]: d["clickCount"] for d in data}
    # 把原本的資料變成 dict，key 是日期字串，value 是點擊次數
    # 方便後續查詢，有的就用原本數據，沒有的自動補 0

    filled = [
        {"day": d.strftime("%m-%d"),
         "clickCount": data_dict.get(d.isoformat(), 0)}
        for d in date_range
    ]
    # 走訪每一天，把有資料的天寫進來，沒資料的就自動補 0

    return filled
