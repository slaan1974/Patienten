from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Date, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from database import Base


class KindcheckForm(Base):
    __tablename__ = "kindcheck_forms"
    __table_args__ = (UniqueConstraint("patient_id", name="uq_patient_kindcheck_form"),)

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    datum = Column(Date, nullable=True)
    herkomst = Column(String, nullable=True)
    herkomst_anders = Column(Text, nullable=True)
    kleinstiefpleeg = Column(String, nullable=True)
    opkomst = Column(Boolean, nullable=True)
    opmerking_gedeelde_zorg = Column(Text, nullable=True)
    opmerking_alleen_zorg = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
