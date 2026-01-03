"""Unit tests for group selection service."""

from unittest.mock import AsyncMock, Mock, create_autospec

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.group import Group
from src.models.speciality import Speciality
from src.repositories.group_repo import GroupRepository
from src.repositories.speciality_repo import SpecialityRepository
from src.repositories.subgroup_repo import SubgroupRepository
from src.services.group_selection_service import GroupSelectionService


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_speciality_repo() -> AsyncMock:
    """Create mock SpecialityRepository."""
    return create_autospec(SpecialityRepository, instance=True)


@pytest.fixture
def mock_group_repo() -> AsyncMock:
    """Create mock GroupRepository."""
    return create_autospec(GroupRepository, instance=True)


@pytest.fixture
def mock_subgroup_repo() -> AsyncMock:
    """Create mock SubgroupRepository."""
    return create_autospec(SubgroupRepository, instance=True)


@pytest.fixture
def group_selection_service(
    mock_session: AsyncMock,
    mock_speciality_repo: AsyncMock,
    mock_group_repo: AsyncMock,
    mock_subgroup_repo: AsyncMock,
) -> GroupSelectionService:
    """Create GroupSelectionService with mocked dependencies."""
    return GroupSelectionService(
        session=mock_session,
        speciality_repo=mock_speciality_repo,
        group_repo=mock_group_repo,
        subgroup_repo=mock_subgroup_repo,
    )


class TestGroupSelectionService:
    """Tests for GroupSelectionService."""

    @pytest.mark.asyncio
    async def test_get_all_specialities(
        self,
        group_selection_service: GroupSelectionService,
        mock_speciality_repo: AsyncMock,
    ) -> None:
        """Test get_all_specialities delegates to repo."""
        mock_specialities = []
        mock_speciality_repo.find_all = AsyncMock(return_value=mock_specialities)

        result = await group_selection_service.get_all_specialities()

        mock_speciality_repo.find_all.assert_awaited_once()
        assert result == mock_specialities

    @pytest.mark.asyncio
    async def test_get_courses_by_speciality(
        self,
        group_selection_service: GroupSelectionService,
        mock_group_repo: AsyncMock,
    ) -> None:
        """Test get_courses_by_speciality delegates to repo."""
        mock_courses = [1, 2, 3, 4, 5, 6]
        mock_group_repo.find_distinct_courses = AsyncMock(return_value=mock_courses)

        result = await group_selection_service.get_courses_by_speciality(1)

        mock_group_repo.find_distinct_courses.assert_awaited_once_with(1)
        assert result == mock_courses

    @pytest.mark.asyncio
    async def test_get_streams_by_speciality_course(
        self,
        group_selection_service: GroupSelectionService,
        mock_group_repo: AsyncMock,
    ) -> None:
        """Test get_streams_by_speciality_course delegates to repo."""
        mock_streams = ["ОМ", "ПМ"]
        mock_group_repo.find_distinct_streams = AsyncMock(return_value=mock_streams)

        result = await group_selection_service.get_streams_by_speciality_course(1, 1)

        mock_group_repo.find_distinct_streams.assert_awaited_once_with(1, 1)
        assert result == mock_streams

    @pytest.mark.asyncio
    async def test_get_groups_by_structure(
        self,
        group_selection_service: GroupSelectionService,
        mock_group_repo: AsyncMock,
    ) -> None:
        """Test get_groups_by_structure delegates to repo."""
        mock_groups = []
        mock_group_repo.find_by_speciality_course_stream = AsyncMock(return_value=mock_groups)

        result = await group_selection_service.get_groups_by_structure(1, 1, "ОМ")

        mock_group_repo.find_by_speciality_course_stream.assert_awaited_once_with(1, 1, "ОМ")
        assert result == mock_groups

    @pytest.mark.asyncio
    async def test_get_all_specialities_returns_sequence(
        self,
        group_selection_service: GroupSelectionService,
        mock_speciality_repo: AsyncMock,
    ) -> None:
        """Test get_all_specialities returns a sequence."""
        mock_specialities = []
        mock_speciality_repo.find_all = AsyncMock(return_value=mock_specialities)

        result = await group_selection_service.get_all_specialities()

        assert isinstance(result, (list, tuple))

    @pytest.mark.asyncio
    async def test_hierarchical_selection_flow(
        self,
        group_selection_service: GroupSelectionService,
        mock_speciality_repo: AsyncMock,
        mock_group_repo: AsyncMock,
        mock_subgroup_repo: AsyncMock,
    ) -> None:
        """Test typical hierarchical selection flow."""
        mock_speciality = Mock(Speciality, instance=True)
        mock_speciality.id = 1
        mock_specialities = [mock_speciality]
        mock_courses = [1, 2]
        mock_streams = ["Б"]
        mock_group = Mock(Group, instance=True)
        mock_group.id = 1
        mock_groups = [mock_group]
        mock_subgroups = []

        mock_speciality_repo.find_all = AsyncMock(return_value=mock_specialities)
        mock_group_repo.find_distinct_courses = AsyncMock(return_value=mock_courses)
        mock_group_repo.find_distinct_streams = AsyncMock(return_value=mock_streams)
        mock_group_repo.find_by_speciality_course_stream = AsyncMock(return_value=mock_groups)
        mock_subgroup_repo.find_by_group_id = AsyncMock(return_value=mock_subgroups)

        # Step 1: Get specialities
        specialities = await group_selection_service.get_all_specialities()
        assert list(specialities) == mock_specialities

        # Step 2: Get courses for first speciality
        courses = await group_selection_service.get_courses_by_speciality(1)
        assert list(courses) == mock_courses

        # Step 3: Get streams for first course
        streams = await group_selection_service.get_streams_by_speciality_course(1, 1)
        assert list(streams) == mock_streams

        # Step 4: Get groups for first stream
        groups = await group_selection_service.get_groups_by_structure(1, 1, "Б")
        assert list(groups) == mock_groups

        # Step 5: Get subgroups for first group
        subgroups = await group_selection_service.get_subgroups_by_group(1)
        assert list(subgroups) == mock_subgroups
