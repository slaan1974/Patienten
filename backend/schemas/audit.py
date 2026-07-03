from datetime import datetime
from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    table_name: str
    record_id: int
    action: str
    old_values: str | None
    new_values: str | None
    changed_by: int
    changed_at: datetime
    ip_address: str | None

    class Config:
        from_attributes = True
