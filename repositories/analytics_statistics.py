
from database.model import UrlMapping, EventLog, IpLocation, QRCode, UTMParams
from sqlalchemy import select, func, case, and_, or_
from datetime import datetime, timedelta, timezone, date,  time


# all links peformance
def get_link_performance(db, user_id):
    eventlog_join = and_(
        UrlMapping.id == EventLog.mapping_id,
        EventLog.device_type != "Bot",
        EventLog.app_source != "Bot"
    )

    stmt = (
        select(UrlMapping,
               QRCode,
               func.count(case((EventLog.event_type == "click", 1))
                          ).label("clicks"),
               func.count(case((EventLog.event_type == "scan", 1))
                          ).label("scans"),
               func.count(EventLog.id).label("total_interaction"))
        .outerjoin(EventLog, eventlog_join)
        .outerjoin(QRCode,  QRCode.mappping_url == UrlMapping.id)
        .where(UrlMapping.user_id == user_id,

               )
        .group_by(UrlMapping.id, QRCode.id)
        .order_by(func.count(EventLog.id).desc())
    )
    results = db.execute(stmt).mappings().all()
    link_count, qrcode_count, data = build_link_qrcode_summary(results)
    return {
        "totalLinks": link_count,
        "totalQRCodes": qrcode_count,
        "items": data
    }


def build_link_qrcode_summary(results):
    qrcode_count = 0
    link_count = 0
    data = []

    for row in results:
        link = row.get('UrlMapping')
        qrcode = row.get("QRCode")
        link_count += 1
        if qrcode:
            qrcode_count += 1
        data.append(
            {
                "link": {
                    "id": link.id,
                    "title": link.title,
                    "shortKey": link.short_key,
                    "uuid": link.uuid,
                    "clicks": row.get("clicks"),
                    "scan": row.get("scans"),
                    "totalInteraction": row.get("total_interaction"),
                    "interactionLevel": get_interaction_level(row.get("total_interaction")),
                    "createdAt": link.created_at.strftime("%Y-%m-%d")
                },
                "qrcode": {
                    "id": qrcode.id if qrcode else None,
                    "createAt": qrcode.created_at.strftime("%Y-%m-%d")if qrcode else None
                }
            }
        )
    return link_count, qrcode_count, data


def get_interaction_level(total: int) -> str:
    if total == 0:
        return "None"
    elif total <= 5:
        return "Low"
    elif total <= 20:
        return "Medium"
    elif total <= 50:
        return "High"
    else:
        return "Very high"


# trending
def get_all_interaction_counts(db, user_id, start_date, end_date):
    today = date.today()
    if not end_date:
        end_date = today
    if not start_date:
        start_date = end_date - timedelta(days=27)
        # print(start_date)
    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)
    stmt = (
        select(
            func.date(EventLog.created_at).label("day"),
            func.count(case((EventLog.event_type == "click", 1))
                       ).label("clicks"),
            func.count(case((EventLog.event_type == "scan", 1))
                       ).label("scans"),
            func.count(EventLog.id).label("total_interaction"),

        )
        .join(UrlMapping, EventLog.mapping_id == UrlMapping.id)
        .where(UrlMapping.user_id == user_id, EventLog.created_at >= start_datetime, EventLog.created_at <= end_datetime,            EventLog.device_type != "Bot",
               EventLog.app_source != "Bot")
        .group_by(func.date(EventLog.created_at))
        .order_by("day")
    )
    results = db.execute(stmt).mappings().all()
    data = {row["day"].strftime("%m-%d"): {"clicks": row["clicks"], "scans": row["scans"],
                                           "total": row["total_interaction"]}for row in results}
    max_day, max_count, trend = all_interaction_fill_missing_dates(
        start_date, end_date, data)
    top_info = get_top_info(db, max_day, user_id)
    return {
        "trend": trend,
        "summary": {
            "max_day": max_day.strftime("%m-%d") if max_day else None,
            "max_count": max_count,
        },
        "top_info": top_info
    }


def all_interaction_fill_missing_dates(start_day: date, end_day: date, data):
    max_day = None
    max_count = 0
    trend = []
    total_days = (end_day - start_day).days + 1
    for i in range(total_days):
        day = start_day + timedelta(days=i)
        day_str = day.strftime("%m-%d")
        data_count = data.get(day_str, {"clicks": 0, "scans": 0, "total": 0})

        if data_count.get("total") > max_count:
            max_count = data_count.get("total")
            max_day = day
        trend.append(
            {
                "day": day_str,
                **data_count
            }
        )
    return max_day, max_count, trend


def get_top_info(db, max_day, user_id):

    stmt = (
        select(
            UrlMapping,
            UTMParams.utm_campaign,
            func.count(case((EventLog.event_type == "click", 1))
                       ).label("clicks"),
            func.count(case((EventLog.event_type == "scan", 1))
                       ).label("scans"),
            func.count(EventLog.id).label("interactions")
        ).select_from(EventLog)
        .join(UrlMapping, EventLog.mapping_id == UrlMapping.id)
        .outerjoin(UTMParams, UrlMapping.id == UTMParams.mapping_id)
        .where(
            UrlMapping.user_id == user_id,
            func.date(EventLog.created_at) == max_day,
            EventLog.device_type != "Bot",
            EventLog.app_source != "Bot"
        )
        .group_by(UrlMapping, UTMParams.utm_campaign)
        .order_by(func.count(EventLog.id).desc())
        # .limit(3)

    )
    results = db.execute(stmt).mappings().all()
    return build_top_info(results)
    # print(results)


def build_top_info(data):
    top_links = []
    for row in (data):
        link = row.get('UrlMapping')
        campaign = row.get('utm_campaign')
        top_links.append(
            {
                "title": link.title,
                "shortKey": link.short_key,
                "uuid": link.uuid,
                "utm_campaign": campaign,
                "clicks": row.clicks,
                "scans": row.scans,
                "interactions": row.interactions
            }
        )
    return top_links
    # print(top_links)

# click_scan ratio


def get_clicks_and_scans_ratio(db, user_id):
    stmt = (
        select(
            func.count(case((EventLog.event_type == "click", 1))
                       ).label("clicks"),
            func.count(case((EventLog.event_type == "scan", 1))
                       ).label("scans"),
        ).select_from(EventLog)
        .join(UrlMapping, EventLog.mapping_id == UrlMapping.id)
        .where(
            UrlMapping.user_id == user_id,
            EventLog.device_type != "Bot",
            EventLog.app_source != "Bot"
        )
    )
    results = db.execute(stmt).mappings().first()
    if results:
        clicks = results.get("clicks", 0)
        scans = results.get("scans", 0)
        total = clicks + scans

        if total > 0:
            click_percent = round(clicks / total * 100, 2)
            scan_percent = round(scans / total * 100, 2)
        else:
            click_percent = scan_percent = 0.0
    else:
        clicks = scans = total = click_percent = scan_percent = 0
    return {
        "clicks": clicks,
        "scans": scans,
        "total": total,
        "click_percent": click_percent,
        "scan_percent": scan_percent
    }
