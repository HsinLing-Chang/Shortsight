from fastapi import HTTPException
from utils.statistics import fill_missing_dates, get_percent
from database.model import UrlMapping, EventLog, IpLocation
from sqlalchemy import select,  func, desc


async def get_click_location(db, uuid, user_id,  one_month_ago, limit=5):
    try:
        stmt = (
            select(
                IpLocation.country,
                func.count().label("clicks")
            )
            .join(EventLog, EventLog.ip_address == IpLocation.ip_address)
            .join(UrlMapping, EventLog.mapping_id == UrlMapping.id)
            .where(
                UrlMapping.uuid == uuid,
                UrlMapping.user_id == user_id,
                EventLog.event_type == "click",
                EventLog.created_at >= one_month_ago,
            )
            .group_by(IpLocation.country)
            .order_by(desc("clicks"))
            .limit(limit)
        )
        result = db.execute(stmt).mappings().all()
        data = get_percent([dict(row) for row in result], "clicks")
        return data
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


async def get_cliek_event(db, uuid, user_id, one_month_ago):
    try:
        stmt = (
            select(
                func.date(EventLog.created_at).label("day"),
                func.count().label("clickCount")
            )
            .join(UrlMapping, EventLog.mapping_id == UrlMapping.id)
            .where(
                UrlMapping.uuid == uuid,
                UrlMapping.user_id == user_id,
                EventLog.event_type == "click",
                EventLog.created_at >= one_month_ago,
            )
            .group_by(func.date(EventLog.created_at))
            .order_by(func.date(EventLog.created_at))
        )
        result = db.execute(stmt).mappings().all()
        click_events = fill_missing_dates(result, "clickCount")
        # print(click_events)
        return click_events
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


async def get_referrer(db, uuid, user_id, one_month_ago):
    try:
        stmt = (select(
            EventLog.referer,
            func.count().label("clicks")
        ).select_from(EventLog)
            .join(
            UrlMapping,
            EventLog.mapping_id == UrlMapping.id
        )
            .where(
            UrlMapping.uuid == uuid,
            UrlMapping.user_id == user_id,
            EventLog.created_at >= one_month_ago,
            EventLog.event_type == "click",
        )
            .group_by(EventLog.referer)
        )
        result = db.execute(stmt).all()
        data = dict(result)
        # print(data)
        return data
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


async def get_device(db, uuid, user_id, one_month_ago):
    try:
        stmt = (select(
            EventLog.device_type,
            func.count().label("clicks")
        ).select_from(EventLog)
            .join(UrlMapping, EventLog.mapping_id == UrlMapping.id)
            .where(
            UrlMapping.uuid == uuid,
            UrlMapping.user_id == user_id,
            EventLog.created_at >= one_month_ago,
            EventLog.event_type == "click",
        ).group_by(EventLog.device_type)
        )
        result = db.execute(stmt).all()
        data = dict(result)
        # print(data)
        return data
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


def summary_referrer(rows):
    CHANNELS = [
        "Direct",
        "Organic Search",
        "Organic Social",
        "Organic Video",
        "Referral",
    ]

    channel_map = {
        ch: {"channel": ch, "total_clicks": 0, "sources": []}
        for ch in CHANNELS
    }
    # source 快速索引
    source_lookup = {ch: {} for ch in CHANNELS}

    for row in rows:
        channel = row["channel"] or "Direct"
        source = row["source"] or "(direct)"
        medium = row["medium"] or "(none)"
        domain = row["domain"] or "(none)"
        clicks = row["clicks"]

        ch_obj = channel_map[channel]

        ch_obj["total_clicks"] += clicks

        src_key = (source, medium)
        sources = source_lookup[channel]
        if src_key not in sources:
            src_obj = {
                "source": source,
                "medium": medium,
                "total_clicks": 0,
                "domains": []
            }
            sources[src_key] = src_obj
            ch_obj["sources"].append(src_obj)
        else:
            src_obj = sources[src_key]

        src_obj["total_clicks"] += clicks
        src_obj["domains"].append({
            "domain": domain,
            "clicks": clicks
        })

    result = {
        "channels": [channel_map[ch] for ch in CHANNELS]
    }
    return result
