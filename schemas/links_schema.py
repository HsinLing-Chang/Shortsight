from pydantic import BaseModel,  HttpUrl, ConfigDict,  field_serializer, RootModel, field_validator
from typing import Annotated, Optional
from fastapi import HTTPException
from datetime import datetime
import re


class URLForm(BaseModel):
    title: str
    short_key: Optional[str] = None
    target_url:  HttpUrl

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


class LinkResponse(BaseModel):
    id: int
    user_id: int
    title: str
    uuid: str
    short_key: str | None
    target_url: str
    created_at:  datetime
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at")
    def _fmt_created_at(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")


class LinkListResponse(RootModel):
    root: list[LinkResponse]
