from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.group_repo import GroupRepository
from repositories.lesson_repo import LessonRepository
from repositories.speciality_repo import SpecialityRepository
from repositories.subgroup_repo import SubgroupRepository
from repositories.user_repo import UserRepository


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_speciality_repo(
        self,
        session: AsyncSession,
    ) -> SpecialityRepository:
        return SpecialityRepository(session)

    @provide
    def provide_group_repo(
        self,
        session: AsyncSession,
    ) -> GroupRepository:
        return GroupRepository(session)

    @provide
    def provide_subgroup_repo(
        self,
        session: AsyncSession,
    ) -> SubgroupRepository:
        return SubgroupRepository(session)

    @provide
    def provide_lesson_repo(
        self,
        session: AsyncSession,
    ) -> LessonRepository:
        return LessonRepository(session)

    @provide
    def provide_user_repo(
        self,
        session: AsyncSession,
    ) -> UserRepository:
        return UserRepository(session)
