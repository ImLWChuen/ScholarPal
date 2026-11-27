from __future__ import annotations

from app.domain.applications_interviews.models import Application, AwardOffer
from app.repositories.base import ScopedRepository


class OfferRepository(ScopedRepository[AwardOffer]):
    """Repository for application award offers scoped via application.student_id."""

    def __init__(self) -> None:
        super().__init__(
            model=AwardOffer,
            parent_model=Application,
            parent_fk="application_id",
            parent_owner_field="student_id",
        )


offer_repository = OfferRepository()

