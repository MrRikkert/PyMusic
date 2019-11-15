from pydantic import BaseModel, EmailStr, Schema


class RegisterBase(BaseModel):
    username: str = Schema(..., min_length=5)
    email: EmailStr = Schema(...)


class RegisterIn(RegisterBase):
    """Password must contain atleast one digit, one capital letter and one special character"""

    # regex explained:
    # (?=.*\d): must have atleast one digit
    # (?=.*[A-Z]): must have atleat one capital letter
    # (?=.*[!@#$%^&*()|\\;:.,/\-_+=]): must have atleat one special character
    # All must match atleast once
    password: str = Schema(
        ..., min_length=8, regex=r"(?=.*\d)(?=.*[A-Z])(?=.*[!@#$%^&*()|\\;:.,/\-_+=])"
    )


class RegisterOut(RegisterBase):
    pass


class UserToken(BaseModel):
    access_token: str
    token_type: str


class UserTokenData(BaseModel):
    """Data needed for the jwt token generation

    Parameters
    ----------
    iss: str
        Issuer of the claim. defaults to 'PyMusic'

    sub: str
        Subject of the token. Use username here
    """

    iss: str = "PyMusic"
    sub: str
