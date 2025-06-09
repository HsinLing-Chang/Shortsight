from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from utils.security import JWTtoken
from utils.statistics import fill_missing_dates, get_percent
from utils.dependencies import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select,  func, desc
from database.model import UrlMapping, EventLog, IpLocation
from pydantic import BaseModel,  field_validator
from datetime import date,  datetime, timedelta, timezone
router = APIRouter(prefix="/api", tags=["report"])


class ClickCountByDay(BaseModel):
    day: str
    clickCount: int

    @field_validator('day',  mode='before')
    def date_to_str(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v


@router.get("/click/report/{uuid}")
async def get_click_log(uuid: str, db: Session = Depends(get_db)):
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=28)
    try:
        click_events = get_cliek_event(db, uuid,  one_month_ago)
        location = get_click_location(db, uuid,  one_month_ago)
        referrer = get_referrer(db, uuid, one_month_ago)
        device = get_device(db, uuid, one_month_ago)
        data = {
            "clickEvents": click_events,
            "location": location,
            "referrer": referrer,
            "device": device
        }

        # print(click_events)
        return JSONResponse(content={"ok": True, "data": data})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


def get_click_location(db, uuid,  one_month_ago, limit=5):
    try:
        stmt = (
            select(
                IpLocation.country,
                func.count().label("clicks")
            )
            .join(EventLog, EventLog.ip_address == IpLocation.ip_address)
            .where(
                EventLog.mapping_id == select(UrlMapping.id).where(
                    UrlMapping.uuid == uuid).scalar_subquery(),
                EventLog.event_type == "click",
                EventLog.created_at >= one_month_ago,
                EventLog.device_type != "Bot",
                EventLog.app_source != "Bot",
            )
            .group_by(IpLocation.country)
            .order_by(desc("clicks"))
            .limit(limit)
        )
        result = db.execute(stmt).mappings().all()
        data = get_percent([dict(row) for row in result])
        return data
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


def get_cliek_event(db, uuid,  one_month_ago):
    try:
        stmt = (
            select(
                func.date(EventLog.created_at).label("day"),
                func.count().label("clickCount")
            )
            .join(UrlMapping, EventLog.mapping_id == UrlMapping.id)
            .where(
                UrlMapping.uuid == uuid,
                EventLog.event_type == "click",
                EventLog.created_at >= one_month_ago,
                EventLog.device_type != "Bot",
                EventLog.app_source != "Bot",
            )
            .group_by(func.date(EventLog.created_at))
            .order_by(func.date(EventLog.created_at))
        )
        result = db.execute(stmt).mappings().all()
        click_events = fill_missing_dates(result)
        # print(click_events)
        return click_events
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


def get_referrer(db, uuid, one_month_ago):
    try:
        stmt = (select(
            EventLog.referer,
            func.count().label("clicks")
        ).select_from(EventLog)
            .join(
            UrlMapping,
            EventLog.mapping_id == UrlMapping.id
        )
            .where(
            UrlMapping.uuid == uuid,
            EventLog.created_at >= one_month_ago,
            EventLog.event_type == "click",
            EventLog.device_type != "Bot",
            EventLog.app_source != "Bot"
        )
            .group_by(EventLog.referer)
        )
        result = db.execute(stmt).all()
        data = dict(result)
        print(data)
        return data
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


def get_device(db, uuid, one_month_ago):
    try:
        stmt = (select(
            EventLog.device_type,
            func.count().label("clicks")
        ).select_from(EventLog)
            .join(UrlMapping, EventLog.mapping_id == UrlMapping.id)
            .where(
            UrlMapping.uuid == uuid,
            EventLog.created_at >= one_month_ago,
            EventLog.event_type == "click",
            EventLog.device_type != "Bot",
            EventLog.app_source != "Bot"
        ).group_by(EventLog.device_type)
        )
        result = db.execute(stmt).all()
        data = dict(result)
        print(data)
        return data
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
