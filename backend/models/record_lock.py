from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from database import Base
from config import settings


class RecordLock(Base):
    __tablename__ = "record_locks"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, nullable=False, index=True)
    record_id = Column(Integer, nullable=False, index=True)
    locked_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    locked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
        + timedelta(minutes=settings.LOCK_TIMEOUT_MINUTES),
    )

    __table_args__ = (
        UniqueConstraint("table_name", "record_id", name="uq_lock_table_record"),
    )
