import hmac
from typing import Any

from fastapi import HTTPException, status


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Placeholder for secure password verification."""
    # In full implementation, uses pwd_context.verify(plain_password, hashed_password)
    return hmac.compare_digest(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Placeholder for secure password hashing."""
    # In full implementation, uses pwd_context.hash(password)
    return password


def verify_student_ownership(resource_owner_id: Any, current_student_id: Any) -> None:
    """
    Enforces Rule 8: Backend enforces record ownership on every student endpoint.
    Raises HTTPException(403) if the resource does not belong to the current authenticated student.
    """
    if str(resource_owner_id) != str(current_student_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to access or modify this record.",
        )
