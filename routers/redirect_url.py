from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from utils.dependencies import get_db
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.model import UrlMapping, EventLog, UTMParams
import uuid
from utils.client_info import get_client_ip, get_client_referer, get_client_device
from Geolocation.geolocation import lookup_ip
from repositories.ip import save_geo_to_db
from utils.sqs import sqs
router = APIRouter(prefix="/s", tags=["redirect_url"])

weird_ip = ["128.203.96.252", "173.252.87.18",
            "66.220.149.112", "173.252.127.23", "31.13.115.3", "66.249.83.103", "27.100.64.229", "27.100.64.229"]


@router.get("/{links}")
async def redirect_url(request: Request, links: str, db: Session = Depends(get_db)):
    try:
        stmt = (select(UrlMapping.id, UrlMapping.uuid, UrlMapping.target_url, UTMParams.utm_source, UTMParams.utm_medium, UTMParams.utm_campaign)
                .outerjoin(UTMParams, UrlMapping.id == UTMParams.mapping_id)
                .where(
            or_(UrlMapping.short_key == links, UrlMapping.uuid == links)))
        url_id, url_uuid, target_url, utm_source, utm_medium, utm_campaign = db.execute(
            stmt).one_or_none()
        if not url_id:
            raise HTTPException(
                status_code=404, detail="short key doesn't exist")

        visitor_id = request.cookies.get(f"ss_visitor_id_s_{url_uuid}")
        recent_click = request.cookies.get(f"ss_recent_click_{url_uuid}")

        response = RedirectResponse(url=target_url)

        if recent_click:
            return RedirectResponse(url=target_url)
        else:
            response.set_cookie(
                f"ss_recent_click_{url_uuid}", "1", max_age=300)

        if not visitor_id:
            visitor_id = str(uuid.uuid4())
            response.set_cookie(f"ss_visitor_id_s_{url_uuid}", visitor_id,
                                httponly=True, secure=False, max_age=60*60*24*365,)

        device_result = get_client_device(request)
        if device_result.get("device_type") == "Bot" or device_result.get("app_source") == "Bot":
            return RedirectResponse(url=target_url)
        traffic_info, referer = get_client_referer(
            request,  utm_source, utm_medium, utm_campaign)
        ip = get_client_ip(request)
        if ip in weird_ip:
            return RedirectResponse(url=target_url)
        print(ip)

        print(f"referrer info: {traffic_info}, referrer: {referer}")
        geolocation_info = lookup_ip(ip)
        save_geo_to_db(db, geolocation_info)

        event_data = {
            "mapping_id":  url_id,
            "visitor_id": visitor_id,
            "event_type": "click",
            "referer": referer,
            "ip_address": ip,
            "device_type": device_result.get("device_type"),
            "device_browser": device_result.get("device_browser"),
            "device_os": device_result.get("device_os"),
            "app_source": device_result.get("app_source"),
            "domain": traffic_info["domain"],
            "source": traffic_info["source"],
            "medium": traffic_info["medium"],
            "campaign": traffic_info["campaign"],
            "channel": traffic_info["channel"],
        }
        sqs.sqs_send_message(event_data)
        # print(geolocation_info)
        # new_Event = EventLog(
        #     mapping_id=url_id,
        #     visitor_id=visitor_id,
        #     event_type="click",
        #     referer=referer,
        #     ip_address=ip,
        #     device_type=device_result.get("device_type"),
        #     device_browser=device_result.get("device_browser"),
        #     device_os=device_result.get("device_os"),
        #     app_source=device_result.get("app_source"),
        #     domain=traffic_info["domain"],
        #     source=traffic_info["source"],
        #     medium=traffic_info["medium"],
        #     campaign=traffic_info["campaign"],
        #     channel=traffic_info["channel"],
        # )
        # db.add(new_Event)
        # db.commit()

        return response
    except HTTPException as e:
        raise e
    except SQLAlchemyError as db_err:
        db.rollback()
        print(f"資料庫操作錯誤: {db_err}")
        raise HTTPException(status_code=500, detail="伺服器資料處理錯誤")
    except Exception as e:
        print(f"未知錯誤：{e}")
        raise HTTPException(status_code=500, detail=str(e))


# @router.get("/l/{links}")
# def redirect_url_loc(request: Request, links: str, db: Session = Depends(get_db)):

#     info, referer = get_client_referer(request)
#     print(f"referrer info: {info}, referrer: {referer}")
#     stmt = select(UrlMapping).where(
#         or_(UrlMapping.short_key == links, UrlMapping.uuid == links))
#     mapping_url = db.execute(stmt).scalar_one_or_none()

#     new_traffic_sourec = EventTrafficSource()

#     response = RedirectResponse(url=target_url)
#     return response
