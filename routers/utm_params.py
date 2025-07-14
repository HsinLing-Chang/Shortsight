from fastapi import APIRouter, Depends,  Query
from fastapi.responses import JSONResponse
from utils.dependencies import get_db
from sqlalchemy import select, distinct
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from utils.security import JWTtoken
from database.model import UrlMapping, UTMParams
from datetime import date
from repositories.utm_params import fetch_sources_medium_by_eventlog_types, fetch_campaign_sources_by_eventlog_types, fetch_campaign_by_eventlog_types, fetch_other_traffic_by_eventlog_types
router = APIRouter(prefix="/api", tags=["Utm"])


@router.get("/report/utm/sources")
async def report_sources_by_event_type(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), event_type: str = "click", start_date: Optional[date] = None, end_date: Optional[date] = None):
    # scan or click source/medium
    # data = await fetch_sources_by_event_type(db, current_user.id, start_date, end_date, event_type)
    data = await fetch_sources_medium_by_eventlog_types(db, current_user.id, start_date, end_date, event_type)
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/report/utm/interactions")
async def report_sources_by_all_interactions(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), start_date: Optional[date] = None, end_date: Optional[date] = None):
    # scan and click source/medium
    # data = await fetch_sources_by_all_interactions(db, start_date, end_date, current_user.id)
    data = await fetch_sources_medium_by_eventlog_types(db, current_user.id, start_date, end_date)
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/report/utm/source/{campaign}")
async def report_campaign_sources_by_event_type(campaign: str, db: Annotated[Session, Depends(get_db)], event_type: str = "click", current_user=Depends(JWTtoken.get_current_user), start_date: Optional[date] = None, end_date: Optional[date] = None):
    # scan or click source/medium with campaign
    # data = await fetch_campaign_sources_by_event_type(
    #     campaign, db, current_user.id, start_date, end_date, event_type)
    data = await fetch_campaign_sources_by_eventlog_types(
        campaign, db, current_user.id, start_date, end_date, event_type)
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/report/utm/interactions/{campaign}")
async def report_campaign_sources_by_all_interactions(campaign: str, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), start_date: Optional[date] = None, end_date: Optional[date] = None):
    # scan and click source/meduium with campaign
    # data = await fetch_campaign_sources_by_all_interactions(db, campaign, start_date, end_date, current_user.id)
    data = await fetch_campaign_sources_by_eventlog_types(campaign, db, current_user.id, start_date, end_date)
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/report/utm/campaigns")
async def get_all_campaign(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None)):
    # data = await get_all_campaign_data(db, current_user.id, start_date, end_date)
    data = await fetch_campaign_by_eventlog_types(db, current_user.id, start_date, end_date)
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/report/utm/campaign")
async def get_campaign_event_summary(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), event_type: str = "click", start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None)):
    # data = await get_campaign_with_type(db, current_user.id, event_type, start_date, end_date)
    data = await fetch_campaign_by_eventlog_types(db, current_user.id, start_date, end_date, event_type)
    return JSONResponse(content={"ok": True, "data": data})


@router.get("/all_campaign")
async def get_all_campaign(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), event_type: str = "click", start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None)):

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
async def get_other_traffic(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None)):
    data = await fetch_other_traffic_by_eventlog_types(
        db, current_user.id, start_date, end_date)
    return JSONResponse(content={"ok": True, "data":  data})


@router.get("/non-campaign-traffic-event-type")
async def get_non_campaign_traffic_event_type(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user), event_type: str = "click", start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None)):
    data = await fetch_other_traffic_by_eventlog_types(
        db, current_user.id, start_date, end_date, event_type)
    return JSONResponse(content={"ok": True, "data": data})
