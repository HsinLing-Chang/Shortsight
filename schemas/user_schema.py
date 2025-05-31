from pydantic import BaseModel, EmailStr, ValidationError, field_validator


class UserSignInForm(BaseModel):
    email: EmailStr
    password: str


class UserInfo(UserSignInForm):
    username: str


class UserUpdateForm(BaseModel):
    username: str | None = None
    password: str | None = None
