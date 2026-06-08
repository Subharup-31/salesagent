"""Principal repository — tenant-scoped access to Principal models.

Provides typed methods so bootstrap/seed code does not need raw select()
calls or direct session.add() for Principal.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.database.models import Principal


class PrincipalRepository:
    """Tenant-scoped data access for Principal.

    Write methods add to the session but never commit — the caller (a Unit of
    Work or a bootstrap seeder) handles commit/rollback at the boundary.

    Args:
        session: SQLAlchemy session (caller manages lifecycle).
        tenant_id: Tenant scope for all queries.
    """

    def __init__(self, session: Session, tenant_id: str) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def get_any(self) -> Principal | None:
        """Return any principal for the tenant, or None.

        Used by idempotent seeding to skip when a principal already exists.
        """
        return self._session.scalars(select(Principal).filter_by(tenant_id=self._tenant_id)).first()

    def create(self, principal: Principal) -> Principal:
        """Persist a new principal within this tenant. Does NOT commit.

        Raises ValueError if principal.tenant_id does not match the repository.
        """
        if principal.tenant_id != self._tenant_id:
            raise ValueError(
                f"Tenant mismatch: principal.tenant_id={principal.tenant_id!r} != repository tenant_id={self._tenant_id!r}"
            )
        self._session.add(principal)
        self._session.flush()
        return principal
