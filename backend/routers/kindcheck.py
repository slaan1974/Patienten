from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.kindcheck import KindcheckFormCreate, KindcheckFormUpdate, KindcheckFormOut
from services.kindcheck_service import (
    get_form_by_patient,
    get_form,
    create_form,
    update_form,
    delete_form,
    serialize_with_kinderen,
)
from services.kindcheck_terminologie import get_terminologie
from middleware.auth_middleware import require_user
from middleware.audit_middleware import audit_create, audit_update, audit_delete, _serialize
from models.patient import Patient
from models.kindcheck_form import KindcheckForm

router = APIRouter(prefix="/api/kindcheck", tags=["kindcheck"])


@router.get("/terminologie")
async def terminologie(
    _=Depends(require_user),
):
    return get_terminologie()


@router.get("/{patient_id}", response_model=KindcheckFormOut | None)
async def read_form_by_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_user),
):
    form = await get_form_by_patient(db, patient_id)
    return form


@router.post("/{patient_id}", response_model=KindcheckFormOut, status_code=201)
async def create_or_update_form(
    patient_id: int,
    data: KindcheckFormCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    data.patient_id = patient_id
    existing = await get_form_by_patient(db, patient_id)
    if existing:
        old_dict = await serialize_with_kinderen(existing)
        for key, value in data.model_dump(exclude={"kinderen"}, exclude_unset=True).items():
            setattr(existing, key, value)
        existing.updated_by = user.id
        form = existing
        await db.commit()
        await db.refresh(form)
        form = await update_form(db, form.id, data, user.id)
        ip = request.client.host if request.client else None
        await audit_update(db, form, old_dict, user.id, ip)
        return form
    else:
        form = await create_form(db, data, user.id)
        ip = request.client.host if request.client else None
        await audit_create(db, form, user.id, ip)
        return form


@router.put("/form/{form_id}", response_model=KindcheckFormOut)
async def update_form_endpoint(
    form_id: int,
    data: KindcheckFormUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    form = await get_form(db, form_id)
    if form is None:
        raise HTTPException(status_code=404, detail="Formulier niet gevonden")
    old_dict = await serialize_with_kinderen(form)
    updated = await update_form(db, form_id, data, user.id)
    ip = request.client.host if request.client else None
    await audit_update(db, updated, old_dict, user.id, ip)
    return updated


@router.delete("/form/{form_id}")
async def delete_form_endpoint(
    form_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    form = await get_form(db, form_id)
    if form is None:
        raise HTTPException(status_code=404, detail="Formulier niet gevonden")
    old_dict = await serialize_with_kinderen(form)
    await delete_form(db, form_id)
    ip = request.client.host if request.client else None
    await audit_delete(db, "kindcheck_forms", form_id, old_dict, user.id, ip)
    return {"detail": "Formulier verwijderd"}


@router.get("/status/all")
async def get_all_forms_status(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_user),
):
    patients_result = await db.execute(select(Patient).order_by(Patient.achternaam))
    patients = list(patients_result.scalars().all())

    forms_result = await db.execute(select(KindcheckForm))
    forms = list(forms_result.scalars().all())
    form_map = {f.patient_id: f for f in forms}

    result = []
    for p in patients:
        form = form_map.get(p.id)
        result.append({
            "patient_id": p.id,
            "voornaam": p.voornaam,
            "achternaam": p.achternaam,
            "bsn": p.bsn,
            "woonplaats": p.woonplaats,
            "has_form": form is not None,
            "form_id": form.id if form else None,
        })
    return result
