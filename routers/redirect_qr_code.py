from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from utils.dependencies import get_db
from utils.security import JWTtoken
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from typing import Annotated
from database.model import UrlMapping, EventLog
from Geolocation.geolocation import lookup_ip
from utils.ip import get_client_ip
from repositories.ip import save_geo_to_db
import uuid

router = APIRouter(prefix="/qr")


@router.get("/{short_key}")
def redirect_qr_code(short_key: str, request: Request, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    visitor_id = request.cookies.get("visitor_id")
    if not visitor_id:
        visitor_id = str(uuid.uuid4())
    ip = get_client_ip(request)
    geolocation_info = lookup_ip(ip)
    save_geo_to_db(db, geolocation_info)
    print(ip)
    print(geolocation_info)
    # stmt = select(UrlMapping).where(
    #     or_(UrlMapping.short_key == short_key, UrlMapping.uuid == short_key))
    # mapping_url = db.execute(stmt).scalar_one_or_none()
    # if not mapping_url:
    #     raise HTTPException(status_code=404, detail="短網址不存在")
