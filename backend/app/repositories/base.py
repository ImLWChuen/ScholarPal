from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic asynchronous base repository providing standard CRUD operations."""

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: Any) -> ModelType | None:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def list_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj: ModelType) -> ModelType:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, id: Any) -> bool:
        obj = await self.get_by_id(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
            return True
        return False


class ScopedRepository(BaseRepository[ModelType]):
    """
    Repository that enforces strict ownership scoping by authenticated user ID.

    Direct ownership:
        Filtered directly on `model.<owner_field> == user_id`.
    Joined ownership:
        Filtered via join on `parent_model` where
        `model.<parent_fk> == parent_model.id` and
        `parent_model.<parent_owner_field> == user_id`.
    """

    def __init__(
        self,
        model: type[ModelType],
        owner_field: str | None = None,
        parent_model: type[Any] | None = None,
        parent_fk: str | None = None,
        parent_owner_field: str = "student_id",
    ) -> None:
        super().__init__(model)
        self.owner_field = owner_field
        self.parent_model = parent_model
        self.parent_fk = parent_fk
        self.parent_owner_field = parent_owner_field

    def apply_ownership_scope(
        self, stmt: Select[tuple[ModelType]], user_id: str
    ) -> Select[tuple[ModelType]]:
        """Applies ownership filter scoping the query to the authenticated user ID."""
        if self.parent_model and self.parent_fk:
            parent_id_attr = self.parent_model.id
            parent_owner_attr = getattr(self.parent_model, self.parent_owner_field)
            model_fk_attr = getattr(self.model, self.parent_fk)
            return stmt.join(self.parent_model, model_fk_attr == parent_id_attr).where(
                parent_owner_attr == user_id
            )
        elif self.owner_field:
            owner_attr = getattr(self.model, self.owner_field)
            return stmt.where(owner_attr == user_id)
        raise ValueError(f"No ownership configuration provided for {self.model.__name__}")

    async def get_by_id_scoped(self, db: AsyncSession, id: Any, user_id: str) -> ModelType | None:
        """
        Fetch record by ID scoped strictly to the authenticated user.
        Returns None if record does not exist OR belongs to another user.
        """
        stmt = select(self.model).where(self.model.id == id)
        stmt = self.apply_ownership_scope(stmt, user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def list_scoped(
        self, db: AsyncSession, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """List records scoped strictly to the authenticated user."""
        stmt = select(self.model)
        stmt = self.apply_ownership_scope(stmt, user_id)
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update_scoped(
        self,
        db: AsyncSession,
        id: Any,
        user_id: str,
        update_data: dict[str, Any] | BaseModel,
    ) -> ModelType | None:
        """
        Update a record scoped strictly to the authenticated user.
        Returns None if record does not exist or belongs to another user.
        """
        obj = await self.get_by_id_scoped(db, id, user_id)
        if not obj:
            return None

        values: dict[str, Any] = (
            update_data.model_dump(exclude_unset=True)
            if isinstance(update_data, BaseModel)
            else dict(update_data)
        )
        immutable_fields = {"id", "user_id", "student_id", "application_id", "created_at"}
        for key, value in values.items():
            if hasattr(obj, key) and key not in immutable_fields:
                setattr(obj, key, value)

        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete_scoped(self, db: AsyncSession, id: Any, user_id: str) -> bool:
        """
        Delete a record scoped strictly to the authenticated user.
        Returns False if record does not exist or belongs to another user.
        """
        obj = await self.get_by_id_scoped(db, id, user_id)
        if not obj:
            return False
        await db.delete(obj)
        await db.commit()
        return True

    async def verify_ownership(self, db: AsyncSession, id: Any, user_id: str) -> bool:
        """Verify whether a record exists and belongs to the authenticated user."""
        obj = await self.get_by_id_scoped(db, id, user_id)
        return obj is not None
