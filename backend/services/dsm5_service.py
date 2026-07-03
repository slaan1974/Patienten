from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.dsm5_form import Dsm5Form
from schemas.dsm5_form import Dsm5FormCreate, Dsm5FormUpdate


async def get_form_by_patient(db: AsyncSession, patient_id: int) -> Dsm5Form | None:
    result = await db.execute(
        select(Dsm5Form).where(Dsm5Form.patient_id == patient_id).order_by(Dsm5Form.id.desc()).limit(1)
    )
    return result.scalar_one_or_none()


async def get_form(db: AsyncSession, form_id: int) -> Dsm5Form | None:
    result = await db.execute(select(Dsm5Form).where(Dsm5Form.id == form_id))
    return result.scalar_one_or_none()


async def create_form(db: AsyncSession, data: Dsm5FormCreate, user_id: int) -> Dsm5Form:
    form = Dsm5Form(
        **data.model_dump(),
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(form)
    await db.commit()
    await db.refresh(form)
    return form


async def update_form(
    db: AsyncSession, form_id: int, data: Dsm5FormUpdate, user_id: int
) -> Dsm5Form | None:
    form = await get_form(db, form_id)
    if form is None:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(form, key, value)
    form.updated_by = user_id
    form.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(form)
    return form


async def delete_form(db: AsyncSession, form_id: int) -> bool:
    form = await get_form(db, form_id)
    if form is None:
        return False
    await db.delete(form)
    await db.commit()
    return True
