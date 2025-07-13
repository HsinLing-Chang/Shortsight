from pydantic import BaseModel,  HttpUrl, field_validator, ConfigDict,  field_serializer, RootModel
from typing import List, Optional
from fastapi import HTTPException
from datetime import datetime
from schemas.utm_params_schema import UTM_form

import re


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
