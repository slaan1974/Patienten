import json
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.audit_log import AuditLog


async def log_change(
    db: AsyncSession,
    table_name: str,
    record_id: int,
    action: str,
    old_values: dict | None,
    new_values: dict | None,
    changed_by: int,
    ip_address: str | None = None,
) -> AuditLog:
    log = AuditLog(
        table_name=table_name,
        record_id=record_id,
        action=action,
        old_values=json.dumps(old_values, default=str) if old_values else None,
        new_values=json.dumps(new_values, default=str) if new_values else None,
        changed_by=changed_by,
        changed_at=datetime.now(timezone.utc),
        ip_address=ip_address,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def get_audit_logs(
    db: AsyncSession,
    table_name: str | None = None,
    action: str | None = None,
    changed_by: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[AuditLog]:
    query = select(AuditLog).order_by(AuditLog.changed_at.desc())

    if table_name:
        query = query.where(AuditLog.table_name == table_name)
    if action:
        query = query.where(AuditLog.action == action)
    if changed_by:
        query = query.where(AuditLog.changed_by == changed_by)
    if date_from:
        query = query.where(AuditLog.changed_at >= datetime.fromisoformat(date_from))
    if date_to:
        query = query.where(AuditLog.changed_at <= datetime.fromisoformat(date_to))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_audit_log(db: AsyncSession, log_id: int) -> AuditLog | None:
    result = await db.execute(select(AuditLog).where(AuditLog.id == log_id))
    return result.scalar_one_or_none()
