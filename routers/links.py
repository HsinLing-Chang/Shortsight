from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from utils.dependencies import get_db
from utils.security import JWTtoken
from database.model import UrlMapping, QRCode, UTMParams
from schemas.links_schema import URLForm, LinkResponse, LinkListResponse
from schemas.utm_params_schema import UTM_form
from typing import Annotated
from utils.uuid_generator import uuid_generator

router = APIRouter(prefix="/api", tags=["links"])


@router.post("/links/shorten")
async def create_short_url(url_form: URLForm, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    """建立新短連結"""
    try:
        # RESERVED_KEYS = ["docs",  "static", "health"]
        # if url_form.short_key in RESERVED_KEYS:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST, detail=f"{url_form.short_key} 是系統保留字，請換一個短碼。")
        uuid = await uuid_generator.generate_uuid()

        # print(url_form.utm_params)
        new_utm_params = url_form.utm_params.to_model() if url_form.utm_params else None
        print(new_utm_params)
        mapping = UrlMapping(user_id=current_user.id, title=url_form.title, uuid=uuid,
                             short_key=url_form.short_key, target_url=str(url_form.target_url), utm=new_utm_params)

        db.add(mapping)
        # 建立UTM參數

        db.commit()
        # data = LinkResponse.model_validate(mapping).model_dump()

        return JSONResponse(content={"ok": True})
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Short link already exists. Please try again.")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/links")
async def get_all_links(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    """獲取所有用戶短連結"""
    try:
        stmt = select(UrlMapping).where(
            UrlMapping.user_id == current_user.id)
        url_mapping_obj = db.execute(stmt).scalars().all()
        data = LinkListResponse.model_validate(
            url_mapping_obj).model_dump() if url_mapping_obj else None
        return JSONResponse(content={"ok": True, "data": data if data else None})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/links/{uuid}")
async def get_link(uuid: str, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    try:
        stmt = select(UrlMapping, QRCode.id, UTMParams).where(UrlMapping.uuid == uuid,
                                                              UrlMapping.user_id == current_user.id).outerjoin(QRCode, QRCode.mappping_url == UrlMapping.id).outerjoin(UTMParams,  UTMParams.mapping_id == UrlMapping.id)
        url_mapping_obj, qrcode_id, utm_data = db.execute(stmt).one_or_none()
        data = LinkResponse.model_validate(
            url_mapping_obj).model_dump() if url_mapping_obj else None
        data["qrcode_id"] = qrcode_id
        if utm_data:
            data["utm_campaign"] = utm_data.utm_campaign
            data["utm_source"] = utm_data.utm_source
            data["utm_medium"] = utm_data.utm_medium

        return JSONResponse(content={"ok": True, "data": data})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/utm/{id}")
async def create_utm(id: int, utm_form: UTM_form, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    utm_data = utm_form.to_model()
    # print(utm_data.utm_campaign, utm_data.utm_medium, utm_data.utm_source)
    new_utm_params = UTMParams(mapping_id=id, utm_campaign=utm_data.utm_campaign,
                               utm_medium=utm_data.utm_medium,  utm_source=utm_data.utm_source)
    db.add(new_utm_params)
    db.commit()
    return JSONResponse(content={"ok": True})


@router.put("/links/{uuid}")
async def update_link(uuid: str, url_form: URLForm, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    try:
        stmt = update(UrlMapping).where(UrlMapping.uuid == uuid, UrlMapping.user_id == current_user.id).values(
            short_key=url_form.short_key, target_url=str(url_form.target_url), title=url_form.title)
        result = db.execute(stmt)
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404, detail="Not Found or Unauthorized")
        return JSONResponse(content={"ok": True}, status_code=status.HTTP_200_OK)
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Short link already exists. Please try again.")
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/links/{uuid}")
async def delete_link(uuid: str, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    try:
        stmt = delete(UrlMapping).where(UrlMapping.uuid == uuid,
                                        UrlMapping.user_id == current_user.id)
        result = db.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404, detail="Not Found or Unauthorized")
        db.commit()
        return JSONResponse(content={"ok": True}, status_code=status.HTTP_200_OK)

    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
