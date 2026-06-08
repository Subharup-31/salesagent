"""Property tag repository — tenant-scoped access to PropertyTag models.

Provides typed methods so bootstrap/seed code does not need raw select()
calls or direct session.add() for PropertyTag.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.database.models import PropertyTag


class PropertyTagRepository:
    """Tenant-scoped data access for PropertyTag.

    Write methods add to the session but never commit — the caller (a Unit of
    Work or a bootstrap seeder) handles commit/rollback at the boundary.

    Args:
        session: SQLAlchemy session (caller manages lifecycle).
        tenant_id: Tenant scope for all queries.
    """

    def __init__(self, session: Session, tenant_id: str) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def get_by_tag_id(self, tag_id: str) -> PropertyTag | None:
        """Get a property tag by its tag_id within the tenant, or None."""
        return self._session.scalars(select(PropertyTag).filter_by(tenant_id=self._tenant_id, tag_id=tag_id)).first()

    def create(self, property_tag: PropertyTag) -> PropertyTag:
        """Persist a new property tag within this tenant. Does NOT commit.

        Raises ValueError if property_tag.tenant_id does not match the repository.
        """
        if property_tag.tenant_id != self._tenant_id:
            raise ValueError(
                f"Tenant mismatch: property_tag.tenant_id={property_tag.tenant_id!r} != repository tenant_id={self._tenant_id!r}"
            )
        self._session.add(property_tag)
        self._session.flush()
        return property_tag
