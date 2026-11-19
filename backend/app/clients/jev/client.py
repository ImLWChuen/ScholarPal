"""
Jev Client Interface (TypeSafe AI) for evidence verification.
Uses Choice primitive to evaluate whether crawled evidence supports extracted claims.
Note: In accordance with Non-negotiable Rule 3, Jev results assist the administrator
and NEVER auto-publish records.
"""

from pydantic import BaseModel

from app.core.config import settings


class JevChoiceOption(str):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class JevVerificationResult(BaseModel):
    verdict: str  # Jev Choice output
    confidence_score: float
    supporting_quote: str | None = None
    reasoning: str | None = None


class JevClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.JEV_API_KEY

    async def verify_evidence(
        self,
        claim: str,
        source_evidence: str,
        choices: list[str] | None = None,
    ) -> JevVerificationResult:
        """
        Placeholder interface: Verifies factual claim against crawled source text using Jev Choice.
        """
        raise NotImplementedError("Jev client will be wired to TypeSafe AI API.")
