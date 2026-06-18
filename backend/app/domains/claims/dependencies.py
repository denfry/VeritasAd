"""Claims domain dependencies - service injection."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.claims.service import ClaimsService

_service: "ClaimsService | None" = None


def get_claims_service() -> "ClaimsService":
    """Get the ClaimsService singleton."""
    global _service
    if _service is None:
        from app.domains.claims.service import ClaimsService

        _service = ClaimsService()
    return _service
