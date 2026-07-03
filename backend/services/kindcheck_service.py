from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.kindcheck_form import KindcheckForm
from models.kindcheck_kind import KindcheckKind
from schemas.kindcheck import KindcheckFormCreate, KindcheckFormUpdate


async def get_form_by_patient(db: AsyncSession, patient_id: int) -> KindcheckForm | None:
    result = await db.execute(
        select(KindcheckForm).where(KindcheckForm.patient_id == patient_id).order_by(KindcheckForm.id.desc()).limit(1)
    )
    form = result.scalar_one_or_none()
    if form:
        form.kinderen = await _get_kinderen(db, form.id)
    return form


async def get_form(db: AsyncSession, form_id: int) -> KindcheckForm | None:
    result = await db.execute(select(KindcheckForm).where(KindcheckForm.id == form_id))
    form = result.scalar_one_or_none()
    if form:
        form.kinderen = await _get_kinderen(db, form.id)
    return form


async def _get_kinderen(db: AsyncSession, form_id: int) -> list[KindcheckKind]:
    result = await db.execute(
        select(KindcheckKind).where(KindcheckKind.form_id == form_id).order_by(KindcheckKind.id)
    )
    return list(result.scalars().all())


async def create_form(db: AsyncSession, data: KindcheckFormCreate, user_id: int) -> KindcheckForm:
    kinderen_data = data.kinderen
    form = KindcheckForm(
        **data.model_dump(exclude={"kinderen"}),
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(form)
    await db.commit()
    await db.refresh(form)

    form.kinderen = await _replace_kinderen(db, form.id, kinderen_data)
    return form


async def update_form(
    db: AsyncSession, form_id: int, data: KindcheckFormUpdate, user_id: int
) -> KindcheckForm | None:
    form = await get_form(db, form_id)
    if form is None:
        return None

    for key, value in data.model_dump(exclude={"kinderen"}, exclude_unset=True).items():
        setattr(form, key, value)
    form.updated_by = user_id
    form.updated_at = datetime.now(timezone.utc)

    if "kinderen" in data.model_dump(exclude_unset=True):
        form.kinderen = await _replace_kinderen(db, form.id, data.kinderen or [])

    await db.commit()
    await db.refresh(form)
    form.kinderen = await _get_kinderen(db, form.id)
    return form


async def _replace_kinderen(db: AsyncSession, form_id: int, kinderen_data: list) -> list[KindcheckKind]:
    existing = await db.execute(
        select(KindcheckKind).where(KindcheckKind.form_id == form_id)
    )
    for kind in existing.scalars().all():
        await db.delete(kind)
    await db.flush()

    kinderen = []
    for kd in kinderen_data:
        kind = KindcheckKind(form_id=form_id, **kd.model_dump())
        db.add(kind)
        kinderen.append(kind)
    await db.flush()
    return kinderen


async def delete_form(db: AsyncSession, form_id: int) -> bool:
    form = await get_form(db, form_id)
    if form is None:
        return False
    await db.delete(form)
    await db.commit()
    return True


async def serialize_with_kinderen(form: KindcheckForm) -> dict:
    d = {}
    for col in form.__table__.columns:
        val = getattr(form, col.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        d[col.name] = val
    if hasattr(form, "kinderen") and form.kinderen:
        d["kinderen"] = [
            {c.name: getattr(k, c.name) for c in KindcheckKind.__table__.columns}
            for k in form.kinderen
        ]
    return d
