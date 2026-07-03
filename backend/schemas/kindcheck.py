from datetime import date
from pydantic import BaseModel


class KindcheckKindCreate(BaseModel):
    kind_naam: str | None = None
    kind_soort: str | None = None
    kind_gebdat: date | None = None
    kind_afhankelijk: bool | None = None
    kind_zorg: str | None = None
    kind_overleden: bool | None = None


class KindcheckKindOut(BaseModel):
    id: int
    form_id: int
    kind_naam: str | None
    kind_soort: str | None
    kind_gebdat: date | None
    kind_afhankelijk: bool | None
    kind_zorg: str | None
    kind_overleden: bool | None

    class Config:
        from_attributes = True


class KindcheckFormCreate(BaseModel):
    patient_id: int
    datum: date | None = None
    herkomst: str | None = None
    herkomst_anders: str | None = None
    kleinstiefpleeg: str | None = None
    opkomst: bool | None = None
    opmerking_gedeelde_zorg: str | None = None
    opmerking_alleen_zorg: str | None = None
    kinderen: list[KindcheckKindCreate] = []


class KindcheckFormUpdate(BaseModel):
    datum: date | None = None
    herkomst: str | None = None
    herkomst_anders: str | None = None
    kleinstiefpleeg: str | None = None
    opkomst: bool | None = None
    opmerking_gedeelde_zorg: str | None = None
    opmerking_alleen_zorg: str | None = None
    kinderen: list[KindcheckKindCreate] | None = None


class KindcheckFormOut(BaseModel):
    id: int
    patient_id: int
    datum: date | None
    herkomst: str | None
    herkomst_anders: str | None
    kleinstiefpleeg: str | None
    opkomst: bool | None
    opmerking_gedeelde_zorg: str | None
    opmerking_alleen_zorg: str | None
    created_by: int
    updated_by: int
    kinderen: list[KindcheckKindOut] = []

    class Config:
        from_attributes = True
