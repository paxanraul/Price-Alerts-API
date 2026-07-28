import app.models # noqa: F401
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.api.deps import get_db
from app.core.config import settings
from app.db.base import Base
from app.main import app


test_engine = create_async_engine(settings.TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(
	test_engine,
	class_=AsyncSession,
	expire_on_commit=False,
)


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
	async with test_engine.begin() as connection:
		await connection.run_sync(Base.metadata.drop_all)
		await connection.run_sync(Base.metadata.create_all)

	yield

	async with test_engine.begin() as connection:
		await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
	async with TestSessionLocal() as session:
		yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
	async def override_get_db():
		yield db_session

	app.dependency_overrides[get_db] = override_get_db

	async with AsyncClient(
		transport=ASGITransport(app=app),
		base_url="http://test",
	) as async_client:
		yield async_client

	app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def close_test_engine():
	yield

	await test_engine.dispose()
