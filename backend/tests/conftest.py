from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.core.db import Base
from app.core.rate_limiter import login_rate_limiter
from app.main import app


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Ensure in-memory login rate limiter is cleared between tests."""
    login_rate_limiter.clear()
    yield
    login_rate_limiter.clear()


@pytest.fixture
async def async_db():
    """Isolated in-memory SQLite database for async endpoint testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield session_factory
    app.dependency_overrides.pop(get_db, None)
    await engine.dispose()


@pytest.fixture
async def async_client(async_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
