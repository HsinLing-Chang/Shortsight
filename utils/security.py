import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from fastapi import Depends, status, HTTPException, Request
# from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from passlib.context import CryptContext
from utils.dependencies import get_user, get_db
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM")


def get_token_from_cookies(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return token


class Hash():
    def hash_password(password):
        hashed_password = pwd_context.hash(password)
        return hashed_password

    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)


class JWTtoken():

    def create_access_token(user_email, expires_delta: timedelta | None = None):

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)

        payload = {
            "email": user_email,
            "exp": expire
        }
        encoded_jwt = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_current_user(db=Depends(get_db), token: str = Depends(get_token_from_cookies)):
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
            user_email = payload.get("email")
            user = await get_user(db, user_email)
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="用戶不存在")
        except InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid credentials")
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Token has expired")
        return user

    async def authenticate_user(user_email: str, password: str,  db=Depends(get_db)):
        user = await get_user(db, user_email)
        if not user:
            return False
        if not Hash.verify_password(password, user.password):
            return False
        return user
