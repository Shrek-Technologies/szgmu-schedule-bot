from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from api.client import ScheduleAPIClient
from repositories.group_repo import GroupRepository
from repositories.lesson_repo import LessonRepository
from repositories.speciality_repo import SpecialityRepository
from repositories.subgroup_repo import SubgroupRepository
from repositories.user_repo import UserRepository
from services.group_selection_service import GroupSelectionService
from services.schedule_service import ScheduleService
from services.settings_service import SettingsService
from services.sync_service import SyncService
from services.user_service import UserService


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_group_selection_service(
        self,
        session: AsyncSession,
        speciality_repo: SpecialityRepository,
        group_repo: GroupRepository,
        subgroup_repo: SubgroupRepository,
    ) -> GroupSelectionService:
        return GroupSelectionService(
            session=session,
            speciality_repo=speciality_repo,
            group_repo=group_repo,
            subgroup_repo=subgroup_repo,
        )

    @provide
    def provide_schedule_service(
        self,
        session: AsyncSession,
        lesson_repo: LessonRepository,
    ) -> ScheduleService:
        return ScheduleService(session=session, lesson_repo=lesson_repo)

    @provide
    def provide_settings_service(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
    ) -> SettingsService:
        return SettingsService(session=session, user_repo=user_repo)

    @provide
    def provide_sync_service(
        self,
        session: AsyncSession,
        api_client: ScheduleAPIClient,
        speciality_repo: SpecialityRepository,
        group_repo: GroupRepository,
        subgroup_repo: SubgroupRepository,
        lesson_repo: LessonRepository,
    ) -> SyncService:
        return SyncService(
            session=session,
            api_client=api_client,
            speciality_repo=speciality_repo,
            group_repo=group_repo,
            subgroup_repo=subgroup_repo,
            lesson_repo=lesson_repo,
        )

    @provide
    def provide_user_service(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
    ) -> UserService:
        return UserService(
            session=session,
            user_repo=user_repo,
        )
