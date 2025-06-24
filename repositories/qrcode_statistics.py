from utils.statistics import fill_missing_dates, get_percent
from database.model import UrlMapping, EventLog, IpLocation, QRCode
from sqlalchemy import select,  func, desc, case
from fastapi import HTTPException


async def get_scan_event(db, id, user_id, one_month_ago):
    try:
        stmt = (
            select(func.date(EventLog.created_at).label("day"),
                   func.count().label("scanCount")
                   )
            .join(QRCode, EventLog.mapping_id == QRCode.mappping_url)
            .join(UrlMapping, QRCode.mappping_url == UrlMapping.id)
            .where(QRCode.id == id,
                   UrlMapping.user_id == user_id,
                   EventLog.event_type == "scan",
                   EventLog.created_at >= one_month_ago,
                   )
            .group_by(func.date(EventLog.created_at))
            .order_by(func.date(EventLog.created_at))
        )
        result = db.execute(stmt).mappings().all()
        scan_events = fill_missing_dates(result, "scanCount")
        return scan_events
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Server error from scan events 'scan count': {str(e)}")


async def get_scan_location(db, id, user_id, one_month_ago, limit=5,):
    try:
        stmt = (
            select(IpLocation.country, func.count().label("scans"))
            .join(EventLog, EventLog.ip_address == IpLocation.ip_address)
            .join(QRCode, EventLog.mapping_id == QRCode.mappping_url)
            .join(UrlMapping, QRCode.mappping_url == UrlMapping.id)
            .where(QRCode.id == id,
                   UrlMapping.user_id == user_id,
                   EventLog.event_type == "scan",
                   EventLog.created_at >= one_month_ago,
                   )
            .group_by(IpLocation.country)
            .order_by(desc("scans"))
            .limit(limit)
        )
        result = db.execute(stmt).mappings().all()
        data = get_percent([dict(row) for row in result], "scans")
        return data
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Server error from scan events 'location': {str(e)}")


async def get_device_browser(db, id, user_id,  one_month_ago):
    browser_group = case(
        (EventLog.device_browser.ilike('%chrome%'), 'Chrome'),
        (EventLog.device_browser.ilike('%safari%'), 'Safari'),
        else_=EventLog.device_browser
    ).label('browser_group')
    try:
        stmt = (
            select(browser_group,
                   func.count().label("scans")
                   )
            .join(QRCode, QRCode.mappping_url == EventLog.mapping_id)
            .join(UrlMapping, QRCode.mappping_url == UrlMapping.id)
            .where(
                QRCode.id == id,
                UrlMapping.user_id == user_id,
                EventLog.event_type == "scan",
                EventLog.created_at >= one_month_ago,
            )
            .group_by(browser_group)
        )
        result = db.execute(stmt).all()
        data = dict(result)
        return data
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Server error from scan events 'device device browser': {str(e)}")


async def get_device_os(db, id,  user_id, one_month_ago):
    try:
        stmt = (
            select(EventLog.device_os,
                   func.count().label("scans")
                   )
            .join(QRCode, QRCode.mappping_url == EventLog.mapping_id)
            .join(UrlMapping, QRCode.mappping_url == UrlMapping.id)
            .where(
                QRCode.id == id,
                EventLog.event_type == "scan",
                UrlMapping.user_id == user_id,
                EventLog.created_at >= one_month_ago,
            )
            .group_by(EventLog.device_os)
        )
        result = db.execute(stmt).all()
        data = dict(result)
        return data
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Server error from scan events 'device OS': {str(e)}")
