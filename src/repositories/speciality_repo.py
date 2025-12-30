from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from models.speciality import EducationLevel, Speciality
from repositories.base import BaseRepository


class SpecialityRepository(BaseRepository):
    """Repository for speciality operations."""

    async def upsert(
        self,
        code: str,
        full_name: str,
        clean_name: str,
        level: EducationLevel | None = None,
    ) -> Speciality:
        """Upsert a speciality."""
        stmt = (
            insert(Speciality)
            .values(
                code=code,
                full_name=full_name,
                clean_name=clean_name,
                level=level,
            )
            .on_conflict_do_update(
                constraint="specialities_full_name_key",
                set_={
                    "code": code,
                    "full_name": full_name,
                    "clean_name": clean_name,
                    "level": level,
                },
            )
            .returning(Speciality)
        )

        result = await self.session.execute(stmt)
        speciality = result.scalar_one()

        await self.session.refresh(speciality)
        return speciality

    async def find_by_id(self, speciality_id: int) -> Speciality | None:
        """Find speciality by ID."""
        stmt = select(Speciality).where(Speciality.id == speciality_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_code(self, code: str) -> Speciality | None:
        """Find speciality by code."""
        stmt = select(Speciality).where(Speciality.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all(self) -> Sequence[Speciality]:
        """Find all specialities."""
        stmt = select(Speciality).order_by(Speciality.code)
        result = await self.session.execute(stmt)
        return result.scalars().all()
