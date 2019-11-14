from pydantic import BaseModel, Schema, EmailStr


class Register(BaseModel):
    username: str = Schema(..., min_length=5)
    email: EmailStr = Schema(...)
    password: str = Schema(...)
