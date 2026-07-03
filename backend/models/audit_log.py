from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, nullable=False, index=True)
    record_id = Column(Integer, nullable=False, index=True)
    action = Column(String, nullable=False)
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    ip_address = Column(String, nullable=True)
