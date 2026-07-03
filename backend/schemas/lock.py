from datetime import datetime
from pydantic import BaseModel


class LockRequest(BaseModel):
    table_name: str
    record_id: int


class LockStatus(BaseModel):
    locked: bool
    locked_by: int | None = None
    locked_by_name: str | None = None
    locked_at: datetime | None = None
    expires_at: datetime | None = None
