from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from utils.dependencies import get_db
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.model import UrlMapping, EventLog, EventTrafficSource
import uuid
from utils.client_info import get_client_ip, get_client_referer, get_client_device
from Geolocation.geolocation import lookup_ip
from repositories.ip import save_geo_to_db
router = APIRouter(prefix="/s")


@router.get("/{links}")
def redirect_url(request: Request, links: str, db: Session = Depends(get_db)):
    try:
        stmt = select(UrlMapping).where(
            or_(UrlMapping.short_key == links, UrlMapping.uuid == links))
        mapping_url = db.execute(stmt).scalar_one_or_none()
        if not mapping_url:
            raise HTTPException(status_code=404, detail="短網址不存在")

        visitor_id = request.cookies.get(f"ss_visitor_id_s_{mapping_url.uuid}")
        if visitor_id:
            return RedirectResponse(url=mapping_url.target_url)
        visitor_id = str(uuid.uuid4())

        ip = get_client_ip(request)
        print(ip)
        traffic_info, referer = get_client_referer(request)
        print(f"referrer info: {traffic_info}, referrer: {referer}")
        geolocation_info = lookup_ip(ip)
        save_geo_to_db(db, geolocation_info)
        device_result = get_client_device(request)
        print(geolocation_info)
        new_Event = EventLog(
            mapping_id=mapping_url.id,
            visitor_id=visitor_id,
            event_type="click",
            referer=referer,
            ip_address=ip,
            device_type=device_result.get("device_type"),
            device_browser=device_result.get("device_browser"),
            device_os=device_result.get("device_os"),
            app_source=device_result.get("app_source"),

            source_info=EventTrafficSource(
                referrer_domain=traffic_info["domain"],
                source=traffic_info["source"],
                medium=traffic_info["medium"],
                channel=traffic_info["channel"],
            )
        )
        db.add(new_Event)
        db.commit()

        response = RedirectResponse(url=mapping_url.target_url)
        response.set_cookie(f"ss_visitor_id_s_{mapping_url.uuid}", visitor_id,
                            httponly=True, secure=False, max_age=30,)
        return response
    except HTTPException as e:
        raise e
    except SQLAlchemyError as db_err:
        db.rollback()
        print(f"資料庫操作錯誤: {db_err}")
        raise HTTPException(status_code=500, detail="伺服器資料處理錯誤")
    except Exception as e:
        print(f"未知錯誤：{e}")
        raise HTTPException(status_code=500, detail="伺服器內部錯誤")


# @router.get("/l/{links}")
# def redirect_url_loc(request: Request, links: str, db: Session = Depends(get_db)):

#     info, referer = get_client_referer(request)
#     print(f"referrer info: {info}, referrer: {referer}")
#     stmt = select(UrlMapping).where(
#         or_(UrlMapping.short_key == links, UrlMapping.uuid == links))
#     mapping_url = db.execute(stmt).scalar_one_or_none()

#     new_traffic_sourec = EventTrafficSource()

#     response = RedirectResponse(url=mapping_url.target_url)
#     return response
