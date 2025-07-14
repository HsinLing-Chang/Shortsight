from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from utils.dependencies import get_db
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.model import UrlMapping, EventLog, UTMParams
import uuid
from repositories.redirect_links import get_link_data
from utils.client_info import get_client_ip, get_client_referer, get_client_device
from Geolocation.geolocation import lookup_ip
from repositories.ip import save_geo_to_db
from utils.sqs import sqs
from services.redirect_service import handle_redirect
import logging
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/s", tags=["redirect_url"])


@router.get("/{links}")
async def redirect_url(request: Request, links: str, db: Session = Depends(get_db)):
    # # stmt = (select(UrlMapping.id, UrlMapping.uuid, UrlMapping.target_url, UTMParams.utm_source, UTMParams.utm_medium, UTMParams.utm_campaign)
    # #         .outerjoin(UTMParams, UrlMapping.id == UTMParams.mapping_id)
    # #         .where(
    # #     or_(UrlMapping.short_key == links, UrlMapping.uuid == links)))
    # url_id, url_uuid, target_url, utm_source, utm_medium, utm_campaign = get_link_data(links, db)
    # if not url_id:
    #     raise HTTPException(
    #         status_code=404, detail="short key doesn't exist")

    # # visitor_id = request.cookies.get(f"ss_visitor_id_s_{url_uuid}")
    # # recent_click = request.cookies.get(f"ss_recent_click_{url_uuid}")

    # # response = RedirectResponse(url=target_url)
    # visitor_id, response = handle_redirect_cookies(request, url_uuid, target_url)
    # if is_recent_click(request, url_uuid):
    #     return RedirectResponse(url=target_url)
    # else:
    #     response.set_cookie(
    #         f"ss_recent_click_{url_uuid}", "1", max_age=300)

    # # if not visitor_id:
    # #     visitor_id = str(uuid.uuid4())
    # #     response.set_cookie(f"ss_visitor_id_s_{url_uuid}", visitor_id,
    # #                         httponly=True, secure=False, max_age=60*60*24*365,)

    # device_result = get_client_device(request)
    # if device_result.get("device_type") == "Bot" or device_result.get("app_source") == "Bot":
    #     return RedirectResponse(url=target_url)
    # traffic_info, referer = get_client_referer(
    #     request,  utm_source, utm_medium, utm_campaign)
    # ip = get_client_ip(request)
    # if ip in weird_ip:
    #     return RedirectResponse(url=target_url)
    # print(ip)

    # print(f"referrer info: {traffic_info}, referrer: {referer}")
    # geolocation_info = lookup_ip(ip)
    # save_geo_to_db(db, geolocation_info)

    # event_data = {
    #     "mapping_id":  url_id,
    #     "visitor_id": visitor_id,
    #     "event_type": "click",
    #     "referer": referer,
    #     "ip_address": ip,
    #     "device_type": device_result.get("device_type"),
    #     "device_browser": device_result.get("device_browser"),
    #     "device_os": device_result.get("device_os"),
    #     "app_source": device_result.get("app_source"),
    #     "domain": traffic_info["domain"],
    #     "source": traffic_info["source"],
    #     "medium": traffic_info["medium"],
    #     "campaign": traffic_info["campaign"],
    #     "channel": traffic_info["channel"],
    # }
    # sqs.sqs_send_message(event_data)

    # return response
    return handle_redirect(links, request, db)
