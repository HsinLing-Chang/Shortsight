from sqlalchemy.orm import Session
from database.model import IpLocation
from fastapi import HTTPException


def save_geo_to_db(db: Session, geo_info):
    try:
        if geo_info:
            new_ip_info = IpLocation(**geo_info)
            db.add(new_ip_info)
            db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
