from pydantic import BaseModel, Schema, EmailStr


class RegisterBase(BaseModel):
    username: str = Schema(..., min_length=5)
    email: EmailStr = Schema(...)


class RegisterIn(RegisterBase):
    password: str = Schema(...)


class RegisterOut(RegisterBase):
    pass


class UserToken(BaseModel):
    access_token: str
    token_type: str


class UserTokenData(BaseModel):
    iss: str
    sub: str
