from schemas.utm_params_schema import UTM_form
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel,  HttpUrl, field_validator
from database.model import UrlMapping, QRCode
from utils.dependencies import get_db
from utils.security import JWTtoken
from utils.S3 import aws_s3
from sqlalchemy.orm import Session, selectinload,  joinedload
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from typing import Annotated, List, Optional
from utils.uuid_generator import uuid_generator
import qrcode
from datetime import datetime
import re
import io
from utils.S3 import aws_s3
from pydantic import ConfigDict,  field_serializer, RootModel
router = APIRouter(prefix="/api", tags=['qrcodes'])


class QrcodeForm(BaseModel):
    title: str
    short_key: Optional[str] = None
    target_url:  HttpUrl
    utm_params: Optional[UTM_form] = None

    @field_validator("short_key")
    def vaildate_short_key(cls, val):
        if val is None:
            return val
        if len(val) > 30:
            raise HTTPException(
                status_code=400, detail="Custom url must not exceed 30 characters in length.")
        if not re.match(r'^[A-Za-z0-9_-]+$', val):
            raise HTTPException(status_code=400,
                                detail="Custom url may only contain English letters, numbers, underscores (_), or hyphens (-).")
        return val


class QrcodeResponse(BaseModel):
    id: int
    mappping_url: int
    image_path: str
    created_at:  datetime
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at")
    def _fmt_created_at(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")


class LinkWithQRcodeResponse(BaseModel):
    id: int
    user_id: int
    title: str
    uuid: str
    short_key: str | None
    target_url: str
    created_at:  datetime
    qr_code: QrcodeResponse
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at")
    def _fmt_created_at(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")


class LinkWithQRcodeListResponse(RootModel):
    root: List[LinkWithQRcodeResponse]


class UpdateQrcode(BaseModel):
    title: str


def create_qrcode_image(uuid):
    try:
        url = f"https://s.ppluchuli.com/qr/{uuid}"
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/qrcodes")
async def create_qr_code(url_form: QrcodeForm, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    if url_form.short_key:
        stmt = select(UrlMapping.short_key).where(
            UrlMapping.short_key == url_form.short_key)
        existing = db.execute(stmt).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Shork link 已存在")
    try:
        uuid = await uuid_generator.generate_uuid()
        image_bytes = create_qrcode_image(uuid)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"QR code 生成失敗: {e}"
        )
    try:
        CDN_path = await aws_s3.upload_qrcode(uuid, image_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"上傳至 S3 失敗: {e}"
        )
    try:
        new_utm_params = url_form.utm_params.to_model() if url_form.utm_params else None
        new_URL_and_QRcode = UrlMapping(user_id=current_user.id, title=url_form.title, uuid=uuid,
                                        short_key=url_form.short_key, target_url=str(url_form.target_url), utm=new_utm_params, qr_code=QRCode(image_path=CDN_path))
        db.add(new_URL_and_QRcode)
        db.commit()
        data = LinkWithQRcodeResponse.model_validate(
            new_URL_and_QRcode).model_dump()
        return JSONResponse(content={"ok": True, "data": data})
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Link已存在，請重新嘗試")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/qrcodes")
async def get_all_qrcodes(db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    stmt = select(UrlMapping).options(joinedload(UrlMapping.qr_code, innerjoin=True)).where(
        UrlMapping.user_id == current_user.id)
    url_mapping_obj = db.execute(stmt).scalars().all()

    data = LinkWithQRcodeListResponse.model_validate(
        url_mapping_obj).model_dump() if url_mapping_obj else None

    return JSONResponse(content={"ok": True, "data": data})


@router.get("/qrcodes/{id}")
def get_qrcode(id: int, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    stmt = select(UrlMapping).options(joinedload(UrlMapping.qr_code, innerjoin=True)).where(
        UrlMapping.user_id == current_user.id, UrlMapping.qr_code.has(id=id))
    url_mapping_obj = db.execute(stmt).scalar_one_or_none()

    data = LinkWithQRcodeResponse.model_validate(
        url_mapping_obj).model_dump() if url_mapping_obj else None

    return JSONResponse(content={"ok": True, "data": data})


@router.put("/qrcodes/{id}")
async def update_qrcode(id: int, update_qrcode: UpdateQrcode, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    stmt = update(UrlMapping).where(UrlMapping.id == id,
                                    UrlMapping.user_id == current_user.id).values(title=update_qrcode.title)
    result = db.execute(stmt)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404, detail="Not Found or Unauthorized")
    return JSONResponse(content={"ok": True})


@router.delete("/qrcodes/{id}")
async def delete_qrcode(id: int, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    uuid = db.execute(select(UrlMapping.uuid).where(
        UrlMapping.qr_code.has(id=id), UrlMapping.user_id == current_user.id)).scalar_one_or_none()
    stmt = delete(QRCode).where(QRCode.id == id,
                                QRCode.mapping.has(user_id=current_user.id))
    result = db.execute(stmt)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404, detail="Not Found or Unauthorized")

    await aws_s3.delete_qrcode(uuid)

    return JSONResponse(content={"ok": True})


@router.post("/qrcodes/{uuid}")
async def create_other_qrcode(uuid: str, db: Annotated[Session, Depends(get_db)], current_user=Depends(JWTtoken.get_current_user)):
    try:
        stmt = select(UrlMapping.id).where(UrlMapping.uuid ==
                                           uuid, UrlMapping.user_id == current_user.id)
        url_id = db.execute(stmt).scalar_one_or_none()
        if not url_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Link not found.")
        image_bytes = create_qrcode_image(uuid)
        CDN_path = await aws_s3.upload_qrcode(uuid, image_bytes)
        new_qrcode = QRCode(mappping_url=url_id, image_path=CDN_path)

        db.add(new_qrcode)
        db.commit()
        qrcode_id = new_qrcode.id
        return JSONResponse(content={"ok": True, "qrcodeId": qrcode_id})
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/qrcode/{uuid}/{format}")
async def get_url(uuid: str, format: str, current_user=Depends(JWTtoken.get_current_user)):
    url = await aws_s3.download_qrcode(uuid, format)
    return url
