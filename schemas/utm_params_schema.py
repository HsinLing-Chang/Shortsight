from pydantic import BaseModel
from typing import Optional
from database.model import UTMParams


class UTM_form(BaseModel):
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None

    def is_empty(self) -> bool:
        return all(getattr(self, field) in (None, "") for field in [
            "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"
        ])

    def to_model(self):
        if not self.is_empty():
            return UTMParams(**self.model_dump())
        return None
