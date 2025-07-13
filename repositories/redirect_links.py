
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, or_
from fastapi import HTTPException
from database.model import UrlMapping, UTMParams


def get_link_data(links, db):
    try:
        stmt = (select(UrlMapping.id, UrlMapping.uuid, UrlMapping.target_url, UTMParams.utm_source, UTMParams.utm_medium, UTMParams.utm_campaign)
                .outerjoin(UTMParams, UrlMapping.id == UTMParams.mapping_id)
                .where(
            or_(UrlMapping.short_key == links, UrlMapping.uuid == links)))
        return db.execute(stmt).one_or_none()
        # if not url_id:
        #     raise HTTPException(
        #         status_code=404, detail="short key doesn't exist")
        # return url_id, url_uuid, target_url, utm_source, utm_medium, utm_campaign
    except SQLAlchemyError as db_err:
        db.rollback()
        print(f"資料庫操作錯誤: {db_err}")
        raise HTTPException(status_code=500, detail="伺服器資料處理錯誤")
    except Exception as e:
        print(f"未知錯誤：{e}")
        raise HTTPException(status_code=500, detail=str(e))
