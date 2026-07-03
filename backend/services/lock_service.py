from datetime import datetime, timezone, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import StaleDataError

from models.record_lock import RecordLock
from models.user import User
from config import settings


async def acquire_lock(db: AsyncSession, table_name: str, record_id: int, user_id: int) -> RecordLock | None:
    existing = await get_lock(db, table_name, record_id)
    if existing:
        if existing.locked_by == user_id:
            existing.expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.LOCK_TIMEOUT_MINUTES)
            try:
                await db.commit()
            except StaleDataError:
                await db.rollback()
                return None
            return existing
        return None
    lock = RecordLock(
        table_name=table_name,
        record_id=record_id,
        locked_by=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.LOCK_TIMEOUT_MINUTES),
    )
    db.add(lock)
    try:
        await db.commit()
        await db.refresh(lock)
    except Exception:
        await db.rollback()
        return None
    return lock


async def release_lock(db: AsyncSession, table_name: str, record_id: int, user_id: int) -> bool:
    lock = await get_lock(db, table_name, record_id)
    if lock is None or lock.locked_by != user_id:
        return False
    await db.delete(lock)
    try:
        await db.commit()
    except StaleDataError:
        await db.rollback()
        return False
    return True


async def get_lock(db: AsyncSession, table_name: str, record_id: int) -> RecordLock | None:
    result = await db.execute(
        select(RecordLock).where(
            and_(
                RecordLock.table_name == table_name,
                RecordLock.record_id == record_id,
                RecordLock.expires_at > datetime.now(timezone.utc),
            )
        )
    )
    return result.scalar_one_or_none()


async def get_lock_with_user(db: AsyncSession, table_name: str, record_id: int) -> dict:
    lock = await get_lock(db, table_name, record_id)
    if lock is None:
        return {"locked": False}
    user_result = await db.execute(select(User).where(User.id == lock.locked_by))
    user = user_result.scalar_one_or_none()
    return {
        "locked": True,
        "locked_by": lock.locked_by,
        "locked_by_name": user.display_name if user else None,
        "locked_at": lock.locked_at,
        "expires_at": lock.expires_at,
    }


async def refresh_lock(db: AsyncSession, table_name: str, record_id: int, user_id: int) -> bool:
    lock = await get_lock(db, table_name, record_id)
    if lock is None or lock.locked_by != user_id:
        return False
    lock.expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.LOCK_TIMEOUT_MINUTES)
    try:
        await db.commit()
    except StaleDataError:
        await db.rollback()
        return False
    return True


async def release_all_user_locks(db: AsyncSession, user_id: int) -> list[dict]:
    result = await db.execute(
        select(RecordLock).where(
            and_(
                RecordLock.locked_by == user_id,
                RecordLock.expires_at > datetime.now(timezone.utc),
            )
        )
    )
    locks = list(result.scalars().all())
    released = []
    for lock in locks:
        released.append({"table_name": lock.table_name, "record_id": lock.record_id})
        await db.delete(lock)
    try:
        await db.commit()
    except StaleDataError:
        await db.rollback()
    return released


async def cleanup_expired_locks(db: AsyncSession) -> None:
    result = await db.execute(
        select(RecordLock).where(RecordLock.expires_at <= datetime.now(timezone.utc))
    )
    expired = list(result.scalars().all())
    for lock in expired:
        await db.delete(lock)
    try:
        await db.commit()
    except StaleDataError:
        await db.rollback()
