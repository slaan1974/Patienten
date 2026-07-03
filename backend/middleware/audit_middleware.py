import json
from datetime import datetime, timezone
from collections.abc import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from models.patient import Patient
from models.dsm5_form import Dsm5Form
from services.audit_service import log_change


def diff_values(old: dict, new: dict) -> tuple[dict, dict]:
    changed_old = {}
    changed_new = {}
    for key in new:
        if key in ("created_by", "updated_by", "created_at", "updated_at", "id"):
            continue
        old_val = old.get(key)
        new_val = new.get(key)
        if old_val != new_val:
            changed_old[key] = old_val
            changed_new[key] = new_val
    return changed_old, changed_new


async def audit_create(db: AsyncSession, instance, user_id: int, ip: str | None = None):
    await log_change(
        db=db,
        table_name=instance.__tablename__,
        record_id=instance.id,
        action="CREATE",
        old_values=None,
        new_values=_serialize(instance),
        changed_by=user_id,
        ip_address=ip,
    )


async def audit_update(db: AsyncSession, instance, old_dict: dict, user_id: int, ip: str | None = None):
    new_dict = _serialize(instance)
    changed_old, changed_new = diff_values(old_dict, new_dict)
    if not changed_new:
        return
    await log_change(
        db=db,
        table_name=instance.__tablename__,
        record_id=instance.id,
        action="UPDATE",
        old_values=changed_old,
        new_values=changed_new,
        changed_by=user_id,
        ip_address=ip,
    )


async def audit_delete(db: AsyncSession, table_name: str, record_id: int, old_dict: dict, user_id: int, ip: str | None = None):
    await log_change(
        db=db,
        table_name=table_name,
        record_id=record_id,
        action="DELETE",
        old_values=old_dict,
        new_values=None,
        changed_by=user_id,
        ip_address=ip,
    )


def _serialize(instance) -> dict:
    d = {}
    for col in instance.__table__.columns:
        val = getattr(instance, col.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        d[col.name] = val
    return d
