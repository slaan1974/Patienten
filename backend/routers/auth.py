from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.user import UserRegister, UserLogin, TokenResponse, UserOut
from services.auth_service import register_user, authenticate_user, create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from models.user import User
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Gebruikersnaam bestaat al")
    user = await register_user(db, data.username, data.password, data.display_name)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.username, data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Ongeldige gebruikersnaam of wachtwoord")
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(token_data: dict, db: AsyncSession = Depends(get_db)):
    from services.auth_service import get_current_user
    refresh_token = token_data.get("refresh_token", "")
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Ongeldig refresh token")
    user_id = int(payload["sub"])
    from sqlalchemy import select
    from models.user import User
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Gebruiker niet gevonden")
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
