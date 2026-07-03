from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        from models.user import User
        from models.patient import Patient
        from models.dsm5_form import Dsm5Form
        from models.kindcheck_form import KindcheckForm
        from models.kindcheck_kind import KindcheckKind
        from models.audit_log import AuditLog
        from models.record_lock import RecordLock
        await conn.run_sync(Base.metadata.create_all)
