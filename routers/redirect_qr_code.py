from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from utils.dependencies import get_db
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from typing import Annotated
from database.model import UrlMapping, EventLog, UTMParams, EventTrafficSource
from Geolocation.geolocation import lookup_ip
from utils.client_info import get_client_ip, get_client_referer, get_client_device
from repositories.ip import save_geo_to_db
import uuid
router = APIRouter(prefix="/qr")


@router.get("/{short_code}")
async def redirect_qr_code(short_code: str, request: Request, db: Annotated[Session, Depends(get_db)]):
    stmt = (select(UrlMapping.id, UrlMapping.uuid, UrlMapping.target_url, UTMParams.utm_source, UTMParams.utm_medium, UTMParams.utm_campaign)
            .outerjoin(UTMParams, UrlMapping.id == UTMParams.mapping_id)
            .where(UrlMapping.uuid == short_code))
    url_id, url_uuid, target_url, utm_source, utm_medium, utm_campaign = db.execute(
        stmt).one_or_none()
    if not url_id:
        raise HTTPException(status_code=404, detail="短網址不存在")
    print(url_id, url_uuid, target_url, utm_source, utm_medium, utm_campaign)
    visitor_id = request.cookies.get(f"ss_visitor_id_qr_{short_code}")
    recent_click = request.cookies.get(f"ss_recent_scan_{url_uuid}")

    response = RedirectResponse(url=target_url)

    if recent_click:
        return RedirectResponse(url=target_url)
    else:
        response.set_cookie(
            f"ss_recent_scan_{url_uuid}", "1", max_age=300)

    if not visitor_id:
        visitor_id = str(uuid.uuid4())
        response.set_cookie(f"ss_visitor_id_qr_{url_uuid}", visitor_id,
                            httponly=True, secure=False, max_age=60*60*24*365,)
    ip = get_client_ip(request)
    print(ip)
    # referer = get_client_referer(request)
    geolocation_info = lookup_ip(ip)
    save_geo_to_db(db, geolocation_info)

    device_result = get_client_device(request)

    if device_result.get("device_type") == "Bot" or device_result.get("app_source") == "Bot":
        return RedirectResponse(url=target_url)

    traffic_info, referer = get_client_referer(
        request,  utm_source, utm_medium, utm_campaign)

    # print(geolocation_info)

    new_Event = EventLog(mapping_id=url_id,
                         visitor_id=visitor_id,
                         event_type="scan",
                         referer=referer,
                         ip_address=ip,
                         device_type=device_result.get("device_type"),
                         device_browser=device_result.get("device_browser"),
                         device_os=device_result.get("device_os"),
                         app_source=device_result.get("app_source"))
    new_eventTraffic = EventTrafficSource(
        mapping_id=url_id,
        domain=traffic_info["domain"],
        source=traffic_info["source"],
        medium=traffic_info["medium"],
        campaign=traffic_info["campaign"],
        channel=traffic_info["channel"],
        event_type="scan",
        visitor_id=visitor_id
    )
    db.add_all([new_Event, new_eventTraffic])
    db.commit()

    return response
