from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from utils.dependencies import get_db
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from typing import Annotated
from database.model import UrlMapping, EventLog
from Geolocation.geolocation import lookup_ip
from utils.client_info import get_client_ip, get_client_referer, get_client_device
from repositories.ip import save_geo_to_db
import uuid
router = APIRouter(prefix="/qr")


@router.get("/{short_code}")
def redirect_qr_code(short_code: str, request: Request, db: Annotated[Session, Depends(get_db)]):
    visitor_id = request.cookies.get("ss_visitor_id")
    stmt = select(UrlMapping).where(UrlMapping.uuid == short_code)
    mapping_url = db.execute(stmt).scalar_one_or_none()
    if not mapping_url:
        raise HTTPException(status_code=404, detail="短網址不存在")
    if visitor_id:
        return RedirectResponse(url=mapping_url.target_url)
    visitor_id = str(uuid.uuid4())
    ip = get_client_ip(request)
    print(ip)
    # referer = get_client_referer(request)
    geolocation_info = lookup_ip(ip)
    save_geo_to_db(db, geolocation_info)
    device_result = get_client_device(request)
    # print("referer:"+referer)
    print(geolocation_info)

    new_Event = EventLog(mapping_id=mapping_url.id,
                         visitor_id=visitor_id, event_type="scan", ip_address=ip, device_type=device_result.get("device_type"), device_browser=device_result.get("device_browser"), device_os=device_result.get("device_os"), app_source=device_result.get("app_source"))
    db.add(new_Event)
    db.commit()

    response = RedirectResponse(url=mapping_url.target_url)
    response.set_cookie("ss_visitor_id", visitor_id,
                        httponly=True, secure=False, max_age=60 * 60 * 24,)
    return response
