from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from utils.security import JWTtoken
from utils.statistics import fill_missing_dates, get_percent
from utils.dependencies import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func, desc
from database.model import UrlMapping, EventLog, IpLocation
from pydantic import BaseModel, ConfigDict, field_validator
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
    try:
        click_events = get_cliek_event(db, uuid)
        location = get_click_location(db, uuid)
        data = {
            "clickEvents": click_events,
            "location": location
        }

        # print(click_events)
        return JSONResponse(content={"ok": True, "data": data})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


def get_click_location(db, uuid, limit=5):
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


def get_cliek_event(db, uuid):
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=28)
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
    # result_list = [
    #     ClickCountByDay(day=day.isoformat(),
    #                     clickCount=clickCount).model_dump()
    #     for day, clickCount in result
    # ]
    click_events = fill_missing_dates(result)
    # print(click_events)
    return click_events
