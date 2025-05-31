from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from utils.dependencies import get_user, get_db
from database.model import User
from schemas.user_schema import UserSignInForm, UserInfo
from utils.security import Hash, JWTtoken
from datetime import timedelta

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/user/signup")
async def signup(user_info: UserInfo, db: Session = Depends(get_db)):
    existing = await get_user(db, user_info.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    try:
        hashed_password = Hash.hash_password(user_info.password)
        new_user = User(username=user_info.username,
                        email=user_info.email, password=hashed_password)
        db.add(new_user)
        db.commit()
        return JSONResponse(content={"ok": True}, status_code=status.HTTP_201_CREATED)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        print(e)


@router.post("/user/signin")
async def signin(response:  Response, user_form: UserSignInForm, db: Session = Depends(get_db), ):
    user = await JWTtoken.authenticate_user(user_form.email, user_form.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password.")
    token = JWTtoken.create_access_token(
        user.email, expires_delta=timedelta(days=7))
    return JSONResponse(content={"ok": True, "token": token})
