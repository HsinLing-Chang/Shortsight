from pydantic import BaseModel
from typing import Optional
from database.model import UTMParams


class UTM_form(BaseModel):
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None

    def is_empty(self) -> bool:
        return all(getattr(self, field) in (None, "") for field in [
            "utm_source", "utm_medium", "utm_campaign"
        ])

    def to_model(self):
        if not self.is_empty():
            # print("非空值")
            data = self.model_dump()
            # print(f"data {data}")
            if data.get("utm_source") in (None, ""):
                data["utm_source"] = "(none)"
            if data.get("utm_medium") in (None, ""):
                data["utm_medium"] = "(none)"
            return UTMParams(**data)
        return None
