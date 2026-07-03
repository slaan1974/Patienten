from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey
from database import Base


class KindcheckKind(Base):
    __tablename__ = "kindcheck_kinderen"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("kindcheck_forms.id", ondelete="CASCADE"), nullable=False, index=True)
    kind_naam = Column(String, nullable=True)
    kind_soort = Column(String, nullable=True)
    kind_gebdat = Column(Date, nullable=True)
    kind_afhankelijk = Column(Boolean, nullable=True)
    kind_zorg = Column(String, nullable=True)
    kind_overleden = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
