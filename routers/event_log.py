from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from utils.security import JWTtoken
from utils.dependencies import get_db
from sqlalchemy.orm import Session
from repositories.link_statistics import get_click_location, get_cliek_event, get_device, get_referrer
from repositories.qrcode_statistics import get_scan_event, get_scan_location, get_device_browser, get_device_os
from typing import Annotated
from datetime import datetime, timedelta, timezone
from database.catch import redis_handler
import json
router = APIRouter(prefix="/api", tags=["report"])


@router.get("/click/report/{uuid}")
async def get_click_log(uuid: str, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=28)
    cache_key = f"click_report:{current_user.id}:{uuid}"
    redis = await redis_handler.get_redis_client()
    cached = await redis.get(cache_key)
    if cached:
        return JSONResponse(content={"ok": True, "data": json.loads(cached), "cached": True})
    try:
        click_events, total = await get_cliek_event(db, uuid,  current_user.id, one_month_ago)
        location = await get_click_location(db, uuid, current_user.id, one_month_ago)
        referrer = await get_referrer(db, uuid, current_user.id, one_month_ago)
        device = await get_device(db, uuid, current_user.id, one_month_ago)
        data = {
            "total": total,
            "clickEvents": click_events,
            "location": location,
            "referrer": referrer,
            "device": device
        }
        await redis.set(cache_key, json.dumps(data), ex=60)
        # print(click_events)
        return JSONResponse(content={"ok": True, "data": data})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scan/report/{id}")
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
        await redis.set(cache_key, json.dumps(data), ex=60)
        return JSONResponse(content={"ok": True, "data": data})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
