from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from utils.security import JWTtoken
from utils.dependencies import get_db
from sqlalchemy.orm import Session
from repositories.link_statistics import get_click_location, get_cliek_event, get_device, get_referrer, summary_referrer
from repositories.qrcode_statistics import get_scan_event, get_scan_location, get_device_browser, get_device_os
from repositories.analytics_statistics import get_link_performance, get_all_interaction_counts, get_clicks_and_scans_ratio
from typing import Annotated, Optional
from datetime import datetime, timedelta, timezone, date, time
from database.catch import redis_handler
import json
from database.model import UrlMapping, EventLog, IpLocation, QRCode, UTMParams, EventTrafficSource
from sqlalchemy import select, func, case
router = APIRouter(prefix="/api", tags=["report"])


@router.get("/report/click/{uuid}")
async def get_click_log(uuid: str, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=28)
    # cache_key = f"click_report:{current_user.id}:{uuid}"
    # redis = await redis_handler.get_redis_client()
    # cached = await redis.get(cache_key)
    # referrer_result = get_referral(db, uuid, current_user.id, one_month_ago)
    # print(referrer_result)
    # if cached:
    #     return JSONResponse(content={"ok": True, "data": json.loads(cached), "cached": True})
    try:
        click_events, total = await get_cliek_event(db, uuid,  current_user.id, one_month_ago)
        location = await get_click_location(db, uuid, current_user.id, one_month_ago)
        # referrer = await get_referrer(db, uuid, current_user.id, one_month_ago)
        device = await get_device(db, uuid, current_user.id, one_month_ago)
        data = {
            "total": total,
            "clickEvents": click_events,
            "location": location,
            # "referrer": referrer,
            "device": device,
            # "referrer_result": referrer_result
        }
        # await redis.set(cache_key, json.dumps(data), ex=30)
        return JSONResponse(content={"ok": True, "data": data})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/click/referrer/{uuid}")
async def get_referrer_data(uuid: str, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    stmt = select(UrlMapping.id).where(
        (UrlMapping.short_key == uuid) | (UrlMapping.uuid ==
                                          uuid), UrlMapping.user_id == current_user.id
    )
    result = db.execute(stmt)
    mapping_id = result.scalar_one_or_none()
    if not mapping_id:
        raise HTTPException(status_code=404, detail="URL not found")

    # 抓出該網址所有 click 的來源資料
    stmt = (
        select(EventTrafficSource.channel,
               EventTrafficSource.source,
               EventTrafficSource.medium,
               EventTrafficSource.domain,
               func.count().label("clicks"))
        .where(
            EventTrafficSource.event_type == "click",
            EventTrafficSource.mapping_id == mapping_id
        ).group_by(
            EventTrafficSource.channel,
            EventTrafficSource.source,
            EventTrafficSource.medium,
            EventTrafficSource.domain
        )
    )
    result = db.execute(stmt).mappings().all()
    summary = summary_referrer(result)
    # print(summary)
    return JSONResponse(content={"ok": True, "data": summary})


@router.get("/report/scan/{id}")
async def get_scan_log(id: int, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=28)
    cache_key = f"click_report:{current_user.id}:{id}"
    redis = await redis_handler.get_redis_client()
    cached = await redis.get(cache_key)
    if cached:
        return JSONResponse(content={"ok": True, "data": json.loads(cached), "cached": True})

    try:

        scan_event, total = await get_scan_event(db, id, current_user.id, one_month_ago)
        location = await get_scan_location(db, id, current_user.id, one_month_ago)
        device_browser = await get_device_browser(db, id, current_user.id, one_month_ago)
        device_os = await get_device_os(db, id, current_user.id, one_month_ago)
        data = {
            "total": total,
            "scanEvents": scan_event,
            "location": location,
            "deviceBrowser": device_browser,
            "deviceOS": device_os
        }
        await redis.set(cache_key, json.dumps(data), ex=30)
        return JSONResponse(content={"ok": True, "data": data})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/performance")
async def get_all_log(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    all_links_data = get_link_performance(db, current_user.id)
    return JSONResponse(content={"ok": True, "data": all_links_data})


@router.get("/report/trend")
async def get_top_trand(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user),  start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None)):
    data = get_all_interaction_counts(
        db, current_user.id, start_date, end_date)
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/report/interaction-ratio")
async def get_all_interaction_ratio(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    data = get_clicks_and_scans_ratio(db, current_user.id)
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/report/referrers")
async def get_all_referrers(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    stmt = (
        select(
            EventLog.referer,
            func.count(EventLog.id).label("clicks")
        )
        .join(UrlMapping, UrlMapping.id == EventLog.mapping_id)
        .where(UrlMapping.user_id == current_user.id,
               EventLog.device_type != "Bot",
               EventLog.app_source != "Bot",
               EventLog.referer.isnot(None))
        .group_by(EventLog.referer)
    )
    results = db.execute(stmt).mappings().all()
    data = [dict(row) for row in results]
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/report/devices")
async def get_all_devices(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    stmt = (
        select(
            EventLog.device_type,
            func.count(EventLog.id).label("counts"),
        )
        .join(UrlMapping, EventLog.mapping_id == UrlMapping.id)
        .where(UrlMapping.user_id == current_user.id,
               EventLog.event_type == "scan",
               EventLog.device_type != "Bot",
               EventLog.app_source != "Bot",
               )
        .group_by(EventLog.device_type)
    )
    results = db.execute(stmt).mappings().all()
    data = [dict(row) for row in results]
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/report/geolocation")
async def get_geolocation_data(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    stmt = (
        select(
            IpLocation.country,
            IpLocation.city,
            IpLocation.latitude,
            IpLocation.longitude,
            func.count(EventLog.id).label("interactions")
        ).select_from(EventLog)
        .join(UrlMapping, EventLog.mapping_id == UrlMapping.id)
        .join(IpLocation, EventLog.ip_address == IpLocation.ip_address)
        .where(
            UrlMapping.user_id == current_user.id,
            EventLog.device_type != "Bot",
            EventLog.app_source != "Bot"
        )
        .group_by(
            IpLocation.country,
            IpLocation.city,
            IpLocation.latitude,
            IpLocation.longitude,
        )
    )
    results = db.execute(stmt).mappings().all()
    data = [dict(row) for row in results]

    return JSONResponse(content={"ok": True, "data": data})


# @router.get("/report/GA")
# async def get_GA_data(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
#     # Channel
#     CHANNELS = ["Direct", "Organic Search",
#                 "Organic Social", "Organic Video", "Referral"]
#     stmt = (
#         select(
#             EventTrafficSource.
#         )
#     )
