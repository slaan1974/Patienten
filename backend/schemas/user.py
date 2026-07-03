from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    password: str
    display_name: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    display_name: str

    class Config:
        from_attributes = True
