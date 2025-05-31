from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from utils.dependencies import get_db
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from database.model import UrlMapping, EventLog
router = APIRouter(prefix="/s")


@router.get("/{links}")
def redirect_url(links: str, db: Session = Depends(get_db)):
    stmt = select(UrlMapping).where(
        or_(UrlMapping.short_key == links, UrlMapping.uuid == links))
    mapping_object = db.execute(stmt).scalar_one_or_none()
    if mapping_object:
        return RedirectResponse(url=mapping_object.target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="短網址不存在，請稍後再試")


def add_click_event(db: Session, mapping_id):
    new_event = EventLog(mapping_id=mapping_id)
