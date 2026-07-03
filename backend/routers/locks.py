from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.lock import LockRequest, LockStatus
from services.lock_service import acquire_lock, release_lock, release_all_user_locks, get_lock_with_user, refresh_lock
from middleware.auth_middleware import require_user
from websocket.manager import manager

router = APIRouter(prefix="/api/lock", tags=["locks"])


@router.post("", response_model=LockStatus)
async def acquire(
    data: LockRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    lock = await acquire_lock(db, data.table_name, data.record_id, user.id)
    if lock is None:
        existing = await get_lock_with_user(db, data.table_name, data.record_id)
        for k, v in existing.items():
            if isinstance(v, datetime):
                existing[k] = v.isoformat()
        raise HTTPException(status_code=423, detail=existing)
    status = await get_lock_with_user(db, data.table_name, data.record_id)
    await manager.notify_lock_changed(data.table_name, data.record_id, user.id, user.display_name, exclude_user_id=user.id)
    return status


@router.delete("")
async def release(
    data: LockRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    success = await release_lock(db, data.table_name, data.record_id, user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Kon lock niet vrijgeven")
    await manager.notify_lock_changed(data.table_name, data.record_id, None, None, exclude_user_id=user.id)
    return {"detail": "Lock vrijgegeven"}


@router.post("/release-all")
async def release_all(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    released = await release_all_user_locks(db, user.id)
    for lock in released:
        await manager.notify_lock_changed(lock["table_name"], lock["record_id"], None, None, exclude_user_id=user.id)
    return {"detail": f"{len(released)} lock(s) vrijgegeven"}


@router.get("/{table_name}/{record_id}", response_model=LockStatus)
async def status(
    table_name: str,
    record_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_user),
):
    return await get_lock_with_user(db, table_name, record_id)


@router.post("/refresh")
async def heartbeat(
    data: LockRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    success = await refresh_lock(db, data.table_name, data.record_id, user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Lock niet gevonden of niet van jou")
    return {"detail": "Lock ververst"}
