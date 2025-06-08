from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from utils.security import JWTtoken
from utils.statistics import fill_missing_dates
from utils.dependencies import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func
from database.model import UrlMapping, EventLog
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
            EventLog.created_at >= one_month_ago
        )
        .group_by(func.date(EventLog.created_at))
        .order_by(func.date(EventLog.created_at))
    )
    click_events = db.execute(stmt).all()
    result_list = [
        ClickCountByDay(day=day.isoformat(),
                        clickCount=clickCount).model_dump()
        for day, clickCount in click_events
    ]
    result = fill_missing_dates(result_list)
    print(result)
    return JSONResponse(content={"ok": True, "data": result})
