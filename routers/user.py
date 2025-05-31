from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from utils.dependencies import get_db
from database.model import User
from utils.security import JWTtoken, Hash
from schemas.user_schema import UserUpdateForm
router = APIRouter(prefix="/api")


@router.get("/user")
async def get_all_user(db: Session = Depends(get_db), user_info=Depends(JWTtoken.get_current_user)):
    print(user_info.username, user_info.id, user_info.email)
    stmt = select(User)
    all_users = db.execute(stmt).scalars().all()
    for user in all_users:
        print(user.username)
    # return  JSONResponse(status_code=status.HTTP)


@router.put("/user")
async def update_user_info(user_form: UserUpdateForm, user_info=Depends(JWTtoken.get_current_user), db: Session = Depends(get_db)):
    new_username = user_form.username if user_form.username else user_info.username
    new_password = Hash.hash_password(
        user_form.password) if user_form.password else user_info.password
    stmt = update(User).where(User.email == user_info.email).values(
        username=new_username, password=new_password)
    db.execute(stmt)
    db.commit()
    return JSONResponse(content={"ok": True}, status_code=status.HTTP_200_OK)


@router.delete("/user")
async def delete_user(user_info=Depends(JWTtoken.get_current_user), db: Session = Depends(get_db)):
    stmt = delete(User).where(User.email == user_info.email)
    db.execute(stmt)
    db.commit()
    return JSONResponse(content={"ok": True}, status_code=status.HTTP_200_OK)
