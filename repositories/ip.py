from sqlalchemy.orm import Session
from database.model import IpLocation
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


def save_geo_to_db(db: Session, geo_info):
    try:
        if geo_info:
            new_ip_info = IpLocation(**geo_info)
            db.add(new_ip_info)
            db.commit()
    except IntegrityError as e:
        db.rollback()
        print("此ip已存在，不需再儲存")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
