from fastapi import APIRouter, Depends, status, HTTPException, Request, Query
from fastapi.responses import RedirectResponse, JSONResponse
from utils.dependencies import get_db
from sqlalchemy import select, func, case, distinct, cast, Float
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql import literal_column
from typing import Annotated, Optional
from utils.security import JWTtoken
from database.model import UrlMapping, EventLog, UTMParams, EventTrafficSource
from datetime import datetime, timedelta, date
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
