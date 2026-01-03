"""Unit tests for API response schemas."""

from src.api.schemas.responses import (
    Pageable,
    PaginatedResponse,
    ScheduleLesson,
    ScheduleStatus,
    XlsxHeader,
    XlsxScheduleSummary,
)


class TestScheduleStatus:
    """Tests for ScheduleStatus model."""

    def test_schedule_status_creation(self) -> None:
        """Test creating ScheduleStatus."""
        status = ScheduleStatus(id=1, name="Current")
        assert status.id == 1
        assert status.name == "Current"


class TestXlsxHeader:
    """Tests for XlsxHeader model."""

    def test_xlsx_header_creation(self) -> None:
        """Test creating XlsxHeader."""
        header = XlsxHeader(
            id=1,
            lesson_type_name="лекционного",
            semester_type="осеннего",
            academic_year="2024/2025",
            course_number="1",
            speciality="Лечебное дело",
            group_stream="ОМ",
        )
        assert header.id == 1
        assert header.semester_type == "осеннего"

    def test_xlsx_header_with_alias(self) -> None:
        """Test XlsxHeader accepts aliased field names."""
        header = XlsxHeader(
            id=1,
            lessonTypeName="лекционного",
            semesterType="осеннего",
            academicYear="2024/2025",
            courseNumber="1",
            speciality="Лечебное дело",
            groupStream="ОМ",
        )
        assert header.lesson_type_name == "лекционного"
        assert header.academic_year == "2024/2025"


class TestXlsxScheduleSummary:
    """Tests for XlsxScheduleSummary model."""

    def test_xlsx_schedule_summary_creation(self) -> None:
        """Test creating XlsxScheduleSummary."""
        header = XlsxHeader(
            id=1,
            lesson_type_name="лекционного",
            semester_type="осеннего",
            academic_year="2024/2025",
            course_number="1",
            speciality="Лечебное дело",
            group_stream="ОМ",
        )
        status = ScheduleStatus(id=1, name="Current")

        summary = XlsxScheduleSummary(
            id=1,
            form_type=1,
            file_name="schedule.xlsx",
            xlsx_header_dto=[header],
            schedule_status=status,
            is_uploaded_from_xlsx=True,
        )
        assert summary.id == 1
        assert summary.file_name == "schedule.xlsx"
        assert len(summary.xlsx_header_dto) == 1


class TestScheduleLesson:
    """Tests for ScheduleLesson model."""

    def test_schedule_lesson_creation(self) -> None:
        """Test creating ScheduleLesson."""
        lesson = ScheduleLesson(
            id=1,
            subject_name="Анатомия",
            pair_time="09:00-10:30",
            department_name="Кафедра анатомии",
            day_name="пн",
            week_number="1",
            group_type_name="лекция",
            lector_name="Иванов И.И.",
            auditory_number="101",
            location_address="Ул. Академическая, 1",
            study_group="ЛД-01",
            subgroup="1п",
            group_stream="ОМ",
            schedule_id=1,
            file_name="schedule.xlsx",
            lesson_type="лекционного",
            error_list=None,
            speciality="Лечебное дело",
            semester="1",
            academic_year="2024/2025",
            course_number="1",
        )
        assert lesson.id == 1
        assert lesson.subject_name == "Анатомия"

    def test_schedule_lesson_with_optional_none(self) -> None:
        """Test ScheduleLesson with optional None values."""
        lesson = ScheduleLesson(
            id=1,
            subject_name="Анатомия",
            pair_time="09:00-10:30",
            department_name=None,
            day_name="пн",
            week_number="1",
            group_type_name=None,
            lector_name=None,
            auditory_number=None,
            location_address=None,
            study_group="ЛД-01",
            subgroup="1п",
            group_stream="ОМ",
            schedule_id=1,
            file_name="schedule.xlsx",
            lesson_type="лекционного",
            error_list=None,
            speciality="Лечебное дело",
            semester="1",
            academic_year="2024/2025",
            course_number="1",
        )
        assert lesson.department_name is None
        assert lesson.lector_name is None


class TestPageable:
    """Tests for Pageable model."""

    def test_pageable_creation(self) -> None:
        """Test creating Pageable."""
        pageable = Pageable(page_number=0, page_size=20)
        assert pageable.page_number == 0
        assert pageable.page_size == 20

    def test_pageable_with_sort(self) -> None:
        """Test Pageable with sort information."""
        pageable = Pageable(page_number=0, page_size=20, sort={"id": True})
        assert pageable.sort == {"id": True}


class TestPaginatedResponse:
    """Tests for PaginatedResponse model."""

    def test_paginated_response_creation(self) -> None:
        """Test creating PaginatedResponse."""
        status = ScheduleStatus(id=1, name="Current")
        header = XlsxHeader(
            id=1,
            lesson_type_name="лекционного",
            semester_type="осеннего",
            academic_year="2024/2025",
            course_number="1",
            speciality="Лечебное дело",
            group_stream="ОМ",
        )
        summary = XlsxScheduleSummary(
            id=1,
            form_type=1,
            file_name="schedule.xlsx",
            xlsx_header_dto=[header],
            schedule_status=status,
            is_uploaded_from_xlsx=True,
        )

        pageable = Pageable(page_number=0, page_size=20)
        response = PaginatedResponse(
            content=[summary],
            pageable=pageable,
            total_elements=1,
            total_pages=1,
            size=1,
            number=0,
            first=True,
            last=True,
            number_of_elements=1,
            empty=False,
        )

        assert len(response.content) == 1
        assert response.total_elements == 1
        assert response.total_pages == 1
        assert response.first is True
        assert response.last is True
