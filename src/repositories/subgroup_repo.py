from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from models.subgroup import Subgroup
from repositories.base import BaseRepository


class SubgroupRepository(BaseRepository):
    """Repository for subgroup operations."""

    async def upsert(
        self,
        group_id: int,
        name: str,
    ) -> Subgroup:
        """Upsert a subgroup."""
        stmt = (
            insert(Subgroup)
            .values(
                group_id=group_id,
                name=name,
            )
            .on_conflict_do_update(
                constraint="uq_subgroups_group_name",
                set_={
                    "group_id": group_id,
                    "name": name,
                },
            )
            .returning(Subgroup)
        )

        result = await self.session.execute(stmt)
        subgroup = result.scalar_one()

        await self.session.refresh(subgroup)
        return subgroup

    async def find_by_id(self, subgroup_id: int) -> Subgroup | None:
        """Find subgroup by ID."""
        stmt = select(Subgroup).where(Subgroup.id == subgroup_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_name_and_group(
        self,
        group_id: int,
        name: str,
    ) -> Subgroup | None:
        """Find a specific subgroup by name and group."""
        stmt = select(Subgroup).where(
            Subgroup.group_id == group_id,
            Subgroup.name == name,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_group(self, group_id: int) -> Sequence[Subgroup]:
        """Find all subgroups for a group."""
        stmt = select(Subgroup).where(Subgroup.group_id == group_id).order_by(Subgroup.name)
        result = await self.session.execute(stmt)
        return result.scalars().all()
