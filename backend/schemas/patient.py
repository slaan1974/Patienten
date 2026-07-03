from datetime import date
from pydantic import BaseModel


class PatientCreate(BaseModel):
    voornaam: str
    achternaam: str
    geboortedatum: date | None = None
    bsn: str | None = None
    adres: str | None = None
    postcode: str | None = None
    woonplaats: str | None = None
    telefoon: str | None = None
    email: str | None = None
    notities: str | None = None


class PatientUpdate(BaseModel):
    voornaam: str | None = None
    achternaam: str | None = None
    geboortedatum: date | None = None
    bsn: str | None = None
    adres: str | None = None
    postcode: str | None = None
    woonplaats: str | None = None
    telefoon: str | None = None
    email: str | None = None
    notities: str | None = None


class PatientOut(BaseModel):
    id: int
    voornaam: str
    achternaam: str
    geboortedatum: date | None
    bsn: str | None
    adres: str | None
    postcode: str | None
    woonplaats: str | None
    telefoon: str | None
    email: str | None
    notities: str | None
    created_by: int
    updated_by: int

    class Config:
        from_attributes = True
