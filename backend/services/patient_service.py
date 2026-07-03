from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.patient import Patient
from schemas.patient import PatientCreate, PatientUpdate


async def get_patients(db: AsyncSession) -> list[Patient]:
    result = await db.execute(select(Patient).order_by(Patient.achternaam))
    return list(result.scalars().all())


async def get_patient(db: AsyncSession, patient_id: int) -> Patient | None:
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    return result.scalar_one_or_none()


async def create_patient(db: AsyncSession, data: PatientCreate, user_id: int) -> Patient:
    patient = Patient(
        **data.model_dump(),
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(patient)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="BSN bestaat al")
    await db.refresh(patient)
    return patient


async def update_patient(
    db: AsyncSession, patient_id: int, data: PatientUpdate, user_id: int
) -> Patient | None:
    patient = await get_patient(db, patient_id)
    if patient is None:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    patient.updated_by = user_id
    patient.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(patient)
    return patient


async def delete_patient(db: AsyncSession, patient_id: int) -> bool:
    patient = await get_patient(db, patient_id)
    if patient is None:
        return False
    await db.delete(patient)
    await db.commit()
    return True
