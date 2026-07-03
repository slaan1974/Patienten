from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.audit import AuditLogOut
from services.audit_service import get_audit_logs, get_audit_log
from middleware.auth_middleware import require_user

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=list[AuditLogOut])
async def list_audit(
    table_name: str | None = Query(None),
    action: str | None = Query(None),
    changed_by: int | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_user),
):
    return await get_audit_logs(db, table_name, action, changed_by, date_from, date_to, skip, limit)


@router.get("/{log_id}", response_model=AuditLogOut)
async def read_audit(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_user),
):
    log = await get_audit_log(db, log_id)
    if log is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Auditlog niet gevonden")
    return log
