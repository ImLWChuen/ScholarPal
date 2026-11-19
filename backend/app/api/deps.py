from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


async def get_current_user_stub() -> dict[str, str]:
    """Dependency placeholder for authenticated user context."""
    return {"id": "student-123", "role": "student"}


async def get_current_student_id(
    current_user: dict[str, str] = Depends(get_current_user_stub),
) -> str:
    """Dependency to retrieve current student ID and enforce ownership."""
    return current_user["id"]
