from pydantic import BaseModel


class Dsm5FormCreate(BaseModel):
    patient_id: int
    status: str = "concept"
    dimensies: str | None = None
    criteria_a: str | None = None
    criteria_b: str | None = None
    criteria_c: str | None = None
    criteria_d: str | None = None
    criteria_e: str | None = None
    conclusie: str | None = None


class Dsm5FormUpdate(BaseModel):
    status: str | None = None
    dimensies: str | None = None
    criteria_a: str | None = None
    criteria_b: str | None = None
    criteria_c: str | None = None
    criteria_d: str | None = None
    criteria_e: str | None = None
    conclusie: str | None = None


class Dsm5FormOut(BaseModel):
    id: int
    patient_id: int
    status: str
    dimensies: str | None
    criteria_a: str | None
    criteria_b: str | None
    criteria_c: str | None
    criteria_d: str | None
    criteria_e: str | None
    conclusie: str | None
    created_by: int
    updated_by: int

    class Config:
        from_attributes = True
