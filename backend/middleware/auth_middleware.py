from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.auth_service import get_current_user

security = HTTPBearer(auto_error=False)


async def require_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Niet geauthenticeerd")
    user = await get_current_user(db, credentials.credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Ongeldig token")
    request.state.user = user
    request.state.token = credentials.credentials
    return user
