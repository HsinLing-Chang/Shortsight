from database.model import Session, User
from sqlalchemy import select


async def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


async def get_user(db, user_email: str):
    try:
        stmt = select(User).where(User.email == user_email)
        user_info = db.execute(stmt).scalar_one_or_none()
        return user_info
    except Exception as e:
        print(e)
