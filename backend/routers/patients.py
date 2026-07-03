from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.patient import PatientCreate, PatientUpdate, PatientOut
from services.patient_service import (
    get_patients,
    get_patient,
    create_patient,
    update_patient,
    delete_patient,
)
from middleware.auth_middleware import require_user
from middleware.audit_middleware import audit_create, audit_update, audit_delete, _serialize

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("", response_model=list[PatientOut])
async def list_patients(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_user),
):
    return await get_patients(db)


@router.get("/{patient_id}", response_model=PatientOut)
async def read_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_user),
):
    patient = await get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patiënt niet gevonden")
    return patient


@router.post("", response_model=PatientOut, status_code=201)
async def create_patient_endpoint(
    data: PatientCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    patient = await create_patient(db, data, user.id)
    ip = request.client.host if request.client else None
    await audit_create(db, patient, user.id, ip)
    return patient


@router.put("/{patient_id}", response_model=PatientOut)
async def update_patient_endpoint(
    patient_id: int,
    data: PatientUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    patient = await get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patiënt niet gevonden")
    old_dict = _serialize(patient)
    updated = await update_patient(db, patient_id, data, user.id)
    ip = request.client.host if request.client else None
    await audit_update(db, updated, old_dict, user.id, ip)
    return updated


@router.delete("/{patient_id}")
async def delete_patient_endpoint(
    patient_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    patient = await get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patiënt niet gevonden")
    old_dict = _serialize(patient)
    await delete_patient(db, patient_id)
    ip = request.client.host if request.client else None
    await audit_delete(db, "patients", patient_id, old_dict, user.id, ip)
    return {"detail": "Patiënt verwijderd"}
