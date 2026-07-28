import app.models # noqa: F401
import pytest_asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.api.deps import get_db
from app.core.config import settings
from app.db.base import Base
from app.api import deps
from app.api.v1 import auth as auth_api
from app.main import app


test_engine = create_async_engine(settings.TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(
	test_engine,
	class_=AsyncSession,
	expire_on_commit=False,
)


class FakeRedis:
	def __init__(self):
		self.data = {}

	async def get(self, key: str):
		return self.data.get(key)

	async def set(self, key: str, value: str, ex: int):
		self.data[key] = value


@pytest.fixture
def fake_redis(monkeypatch):
	fake_redis_client = FakeRedis()

	monkeypatch.setattr(deps, "redis_client", fake_redis_client)
	monkeypatch.setattr(auth_api, "redis_client", fake_redis_client)

	return fake_redis_client


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
