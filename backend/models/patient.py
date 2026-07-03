from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Date, Text, DateTime, ForeignKey
from database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    voornaam = Column(String, nullable=False)
    achternaam = Column(String, nullable=False)
    geboortedatum = Column(Date, nullable=True)
    bsn = Column(String, unique=True, nullable=True)
    adres = Column(String, nullable=True)
    postcode = Column(String, nullable=True)
    woonplaats = Column(String, nullable=True)
    telefoon = Column(String, nullable=True)
    email = Column(String, nullable=True)
    notities = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
