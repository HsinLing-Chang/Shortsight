from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from utils.client_info import get_client_ip, get_client_referer, get_client_device
from repositories.redirect_links import get_link_data
import uuid
from repositories.ip import save_geo_to_db
from Geolocation.geolocation import lookup_ip
from utils.sqs import sqs
from sqlalchemy.exc import SQLAlchemyError

import logging
logger = logging.getLogger(__name__)

weird_ip = ["128.203.96.252", "173.252.87.18",
            "66.220.149.112", "173.252.127.23", "31.13.115.3", "66.249.83.103", "27.100.64.229", "27.100.64.229"]


def handle_redirect_cookies(request: Request, url_uuid: str,  target_url):
    visitor_id = request.cookies.get(f"ss_visitor_id_s_{url_uuid}")
    response = RedirectResponse(url=target_url)
    if not visitor_id:
        visitor_id = str(uuid.uuid4())
        response.set_cookie(f"ss_visitor_id_s_{url_uuid}", visitor_id,
                            httponly=True, secure=False, max_age=60*60*24*365,)
    return visitor_id, response


def is_recent_click(request: Request, uuid: str) -> bool:
    return request.cookies.get(f"ss_recent_click_{uuid}") is not None


def event_data_formatting(url_id, visitor_id, referer, ip, device_result, traffic_info):
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
    return event_data


def handle_redirect(links: str, request: Request, db):
    try:
        url_id, url_uuid, target_url, utm_source, utm_medium, utm_campaign = get_link_data(
            links, db)

        if not url_id:
            raise HTTPException(
                status_code=404, detail="short key doesn't exist")

        visitor_id, response = handle_redirect_cookies(
            request, url_uuid, target_url)

        if is_recent_click(request, url_uuid):
            return RedirectResponse(url=target_url)
        else:
            response.set_cookie(
                f"ss_recent_click_{url_uuid}", "1", max_age=300)

        device_result = get_client_device(request)

        if device_result.get("device_type") == "Bot" or device_result.get("app_source") == "Bot":
            return RedirectResponse(url=target_url)
        traffic_info, referer = get_client_referer(
            request,  utm_source, utm_medium, utm_campaign)

        ip = get_client_ip(request)

        if ip in weird_ip:
            return RedirectResponse(url=target_url)

        geolocation_info = lookup_ip(ip)
        save_geo_to_db(db, geolocation_info)

        event_data = event_data_formatting(
            url_id, visitor_id, referer, ip, device_result, traffic_info)
        sqs.sqs_send_message(event_data)

        return response
    except SQLAlchemyError as db_err:
        db.rollback()
        logger.error(f"[Database Error] {db_err}")
        raise HTTPException(status_code=500, detail="伺服器資料處理錯誤")
    except Exception as e:
        logger.exception(f"[Unknown Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))
