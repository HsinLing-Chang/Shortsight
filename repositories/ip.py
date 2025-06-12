from sqlalchemy.orm import Session
from database.model import IpLocation
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from pydantic import BaseModel


class IpInfor(BaseModel):
    ip: str
    country: str | None
    city: str | None
    latitude: float | None
    longitude: float | None


def save_geo_to_db(db: Session, geo_info):
    try:
        if isinstance(geo_info, dict):
            geo_info = IpInfor(**geo_info)
        if not geo_info or not geo_info.ip:
            raise HTTPException(status_code=400, detail="找不到 IP info")

        stmt = text("""
            INSERT INTO ip_location (ip_address, country, city, latitude, longitude)
            VALUES (:ip, :country, :city, :lat, :lon)
            ON DUPLICATE KEY UPDATE
                country = VALUES(country),
                city = VALUES(city),
                latitude = VALUES(latitude),
                longitude = VALUES(longitude)
        """)
        db.execute(stmt, {
            "ip": geo_info.ip,
            "country": geo_info.country,
            "city": geo_info.city,
            "lat": geo_info.latitude,
            "lon": geo_info.longitude
        })
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
