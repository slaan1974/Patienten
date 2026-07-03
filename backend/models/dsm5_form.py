from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from database import Base


class Dsm5Form(Base):
    __tablename__ = "dsm5_forms"
    __table_args__ = (UniqueConstraint("patient_id", name="uq_patient_dsm5_form"),)

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    status = Column(String, default="concept")
    dimensies = Column(Text, nullable=True)
    criteria_a = Column(Text, nullable=True)
    criteria_b = Column(Text, nullable=True)
    criteria_c = Column(Text, nullable=True)
    criteria_d = Column(Text, nullable=True)
    criteria_e = Column(Text, nullable=True)
    conclusie = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
