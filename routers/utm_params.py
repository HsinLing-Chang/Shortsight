from fastapi import APIRouter, Depends,  Query
from fastapi.responses import JSONResponse
from utils.dependencies import get_db
from sqlalchemy import select, func, case, distinct
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_
from typing import Annotated, Optional
from utils.security import JWTtoken
from database.model import UrlMapping, EventLog, UTMParams
from datetime import timedelta, date
from repositories.utm_params import get_source_medium, get_canpaign_source_medium, get_all_source_interactions, get_campaign_source_interactions, get_all_campaign_data, get_campaign_with_type
router = APIRouter(prefix="/api", tags=["Utm"])


@router.get("/report/utm/sources")
async def get_utm_report(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), event_type: str = "click", start_date: Optional[date] = None, end_date: Optional[date] = None):
    # scan or click source/medium
    data = await get_source_medium(db, current_user.id, start_date, end_date, event_type)
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/report/utm/source/{campaign}")
async def get_campaign_source(campaign: str, db: Annotated[Session, Depends(get_db)], event_type: str = "click", current_user=Depends(JWTtoken.get_current_user), start_date: Optional[date] = None, end_date: Optional[date] = None):
    # scan or click source/medium with campaign
    data = await get_canpaign_source_medium(
        campaign, db, current_user.id, start_date, end_date, event_type)
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/report/utm/interactions")
async def get_interactions(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), start_date: Optional[date] = None, end_date: Optional[date] = None):
    # scan and click source/medium
    data = await get_all_source_interactions(db, start_date, end_date, current_user.id)
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/report/utm/interactions/{campaign}")
async def get_campaign_interactions(campaign: str, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), start_date: Optional[date] = None, end_date: Optional[date] = None):
    # scan and click source/meduium with campaign
    data = await get_campaign_source_interactions(db, campaign, start_date, end_date, current_user.id)
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/report/utm/campaigns")
async def get_all_campaign(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None)):
    data = await get_all_campaign_data(db, current_user.id, start_date, end_date)
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/report/utm/campaign")
async def get_campaign_event_summary(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), event_type: str = "click", start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None)):
    data = await get_campaign_with_type(db, current_user.id, event_type, start_date, end_date)
    return JSONResponse(content={"ok": True, "data": data})


# @router.get("/report/utm/test")
# async def get_campaign_event_summary(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), event_type: str = "click", start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None)):
#     data = await get_campaign_with_type(db, current_user.id, event_type, start_date, end_date)
#     return JSONResponse(content={"ok": True, "data": data})

@router.get("/all_campaign")
def get_all_campaign(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), event_type: str = "click", start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None)):

    stmt = (
        select(distinct(UTMParams.utm_campaign))
        .join(UrlMapping, UrlMapping.id == UTMParams.mapping_id)
        .where(
            UrlMapping.user_id == current_user.id,
            UTMParams.utm_campaign.isnot(None)
        )
    )

    campaigns = db.execute(stmt).scalars().all()
    return JSONResponse(content={"ok": True, "data": campaigns})


@router.get("/non-campaign-traffic")
def get_non_campaign_traffic(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None)):
    first_seen_subq = (
        select(
            EventLog.visitor_id,
            func.min(EventLog.created_at).label("first_seen")
        )
        .where(EventLog.visitor_id.isnot(None))
        .group_by(EventLog.visitor_id)
        .subquery()
    )

    if start_date and end_date:
        new_user_cond = (first_seen_subq.c.first_seen >= start_date) & (
            first_seen_subq.c.first_seen < end_date + timedelta(days=1))
    elif start_date:
        new_user_cond = first_seen_subq.c.first_seen >= start_date
    elif end_date:
        new_user_cond = first_seen_subq.c.first_seen < end_date + \
            timedelta(days=1)
    else:
        new_user_cond = True

    traffic_conditions = []
    if start_date:
        traffic_conditions.append(EventLog.created_at >= start_date)
    if end_date:
        traffic_conditions.append(
            EventLog.created_at < end_date + timedelta(days=1))
    stmt = (select(
        EventLog.source,
        EventLog.medium,
        func.count(EventLog.id).label("total_interactions"),
        func.count(
            distinct(
                case((new_user_cond,  EventLog.visitor_id))
            )
        ).label("new_users")
    )
        .select_from(EventLog)
        .join(UrlMapping, UrlMapping.id == EventLog.mapping_id)
        .outerjoin(first_seen_subq,  EventLog.visitor_id == first_seen_subq.c.visitor_id)
        .where(
        UrlMapping.user_id == current_user.id,
        or_(
            EventLog.campaign.is_(None),
            EventLog.campaign == "",
        ),
        *traffic_conditions
    )
        .group_by(EventLog.source,  EventLog.medium))
    result = db.execute(stmt).mappings().all()
    total_users = sum(row["total_interactions"] for row in result)
    total_new_users = sum(row["new_users"] for row in result)
    overall_ratio = round(total_new_users * 100 /
                          total_users, 1) if total_users else 0.0
    total_level = classify_new_user_ratio(overall_ratio, total_users)
    non_campaign_data = []
    for row in result:
        total = row["total_interactions"]
        new = row["new_users"]
        ratio = round(new * 100 / total, 1) if total else 0.0
        level = classify_new_user_ratio(ratio, total)

        non_campaign_data.append({
            "source": row["source"],
            "medium": row["medium"],
            "total_interactions": total,
            "new_users": new,
            "new_user_ratio": ratio,
            "new_user_level": level
        })
    results = {
        "summary": {
            "total_users": total_users,
            "total_new_users": total_new_users,
            "overall_ratio": overall_ratio,
            "new_user_level": total_level
        },
        "data":  non_campaign_data
    }
    return JSONResponse(content={"ok": True, "data": results})


@router.get("/non-campaign-traffic-event-type")
async def get_non_campaign_traffic_event_type(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), event_type: str = "click", start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None)):
    first_seen_subq = (
        select(
            EventLog.visitor_id,
            func.min(EventLog.created_at).label("first_seen")
        )
        .where(EventLog.visitor_id.isnot(None))
        .group_by(EventLog.visitor_id)
        .subquery()
    )

    if start_date and end_date:
        new_user_cond = (first_seen_subq.c.first_seen >= start_date) & (
            first_seen_subq.c.first_seen < end_date + timedelta(days=1))
    elif start_date:
        new_user_cond = first_seen_subq.c.first_seen >= start_date
    elif end_date:
        new_user_cond = first_seen_subq.c.first_seen < end_date + \
            timedelta(days=1)
    else:
        new_user_cond = True

    traffic_conditions = []
    if start_date:
        traffic_conditions.append(EventLog.created_at >= start_date)
    if end_date:
        traffic_conditions.append(
            EventLog.created_at < end_date + timedelta(days=1))

    if event_type:
        traffic_conditions.append(EventLog.event_type == event_type)

    stmt = (
        select(
            EventLog.source,
            EventLog.medium,
            func.count(EventLog.id).label("total_interactions"),
            func.count(
                distinct(
                    case((new_user_cond,  EventLog.visitor_id))
                )
            ).label("new_users")
        )
        .select_from(EventLog)
        .join(UrlMapping, UrlMapping.id == EventLog.mapping_id)
        .outerjoin(first_seen_subq,  EventLog.visitor_id == first_seen_subq.c.visitor_id)
        .where(
            UrlMapping.user_id == current_user.id,
            or_(
                EventLog.campaign.is_(None),
                EventLog.campaign == "",
            ),
            *traffic_conditions
        )
        .group_by(EventLog.source,  EventLog.medium)
    )

    result = db.execute(stmt).mappings().all()
    total_users = sum(row["total_interactions"] for row in result)
    total_new_users = sum(row["new_users"] for row in result)
    overall_ratio = round(total_new_users * 100 /
                          total_users, 1) if total_users else 0.0
    total_level = classify_new_user_ratio(overall_ratio, total_users)
    non_campaign_data = []
    for row in result:

        total = row["total_interactions"]
        new = row["new_users"]
        ratio = round(new * 100 / total, 1) if total else 0.0
        level = classify_new_user_ratio(ratio, total)

        non_campaign_data.append({
            "source": row["source"],
            "medium": row["medium"],
            "total_interactions": total,
            "new_users": new,
            "new_user_ratio": ratio,
            "new_user_level": level
        })

    results = {
        "summary": {
            "total_users": total_users,
            "total_new_users": total_new_users,
            "overall_ratio": overall_ratio,
            "new_user_level": total_level
        },
        "data":  non_campaign_data
    }
    return JSONResponse(content={"ok": True, "data": results})


def classify_new_user_ratio(ratio: float, total) -> str:
    if total < 5:
        return "Unstable"
    elif ratio >= 70:
        return "Very High"
    elif ratio >= 50:
        return "High"
    elif ratio >= 30:
        return "Moderate"
    elif ratio >= 10:
        return "Low"
    else:
        return "Very Low"
