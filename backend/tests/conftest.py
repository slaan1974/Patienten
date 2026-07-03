import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def demo_user(client: AsyncClient):
    resp = await client.post("/api/auth/register", json={
        "username": "demo",
        "password": "demo123",
        "display_name": "Demo Gebruiker",
    })
    return resp.json()


@pytest_asyncio.fixture
async def demo_token(client: AsyncClient, demo_user):
    resp = await client.post("/api/auth/login", json={
        "username": "demo",
        "password": "demo123",
    })
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(demo_token):
    return {"Authorization": f"Bearer {demo_token}"}


@pytest_asyncio.fixture
async def second_user(client: AsyncClient):
    resp = await client.post("/api/auth/register", json={
        "username": "user2",
        "password": "test123",
        "display_name": "Tweede Gebruiker",
    })
    return resp.json()


@pytest_asyncio.fixture
async def second_token(client: AsyncClient, second_user):
    resp = await client.post("/api/auth/login", json={
        "username": "user2",
        "password": "test123",
    })
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def second_headers(second_token):
    return {"Authorization": f"Bearer {second_token}"}


@pytest_asyncio.fixture
async def test_patient(client: AsyncClient, auth_headers):
    resp = await client.post("/api/patients", json={
        "voornaam": "Stefan",
        "achternaam": "de Vrij",
        "bsn": "648091958",
        "geboortedatum": "2001-01-04",
        "adres": "Comeniusstraat",
        "postcode": "1234AA",
        "woonplaats": "Alkmaar",
        "telefoon": "+123456789",
        "email": "stefan@devrij.nl",
        "notities": "Voetballer",
    }, headers=auth_headers)
    return resp.json()
