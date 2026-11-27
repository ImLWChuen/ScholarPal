from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.profile_preparation.models import StudentProfile
from app.repositories.base import ScopedRepository


class ProfileRepository(ScopedRepository[StudentProfile]):
    """Repository for student profile operations scoped by user_id."""

    def __init__(self) -> None:
        super().__init__(model=StudentProfile, owner_field="user_id")

    async def get_by_user_id(self, db: AsyncSession, user_id: str) -> StudentProfile | None:
        """Retrieve student profile by user_id."""
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_or_create(
        self, db: AsyncSession, user_id: str, default_data: dict[str, Any] | None = None
    ) -> StudentProfile:
        """Retrieve existing profile or create a default empty profile for the student."""
        profile = await self.get_by_user_id(db, user_id)
        if profile:
            return profile

        data = default_data or {}
        new_profile = StudentProfile(
            id=data.get("id", f"prof_{user_id}"),
            user_id=user_id,
            study_level=data.get("study_level"),
            citizenship=data.get("citizenship"),
            state_of_origin=data.get("state_of_origin"),
            cgpa=data.get("cgpa"),
            field_of_study=data.get("field_of_study"),
            household_income=data.get("household_income"),
            academic_results=data.get("academic_results"),
        )
        db.add(new_profile)
        await db.commit()
        await db.refresh(new_profile)
        return new_profile


profile_repository = ProfileRepository()
