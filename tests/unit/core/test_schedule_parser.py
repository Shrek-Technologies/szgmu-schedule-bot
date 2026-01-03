"""Unit tests for schedule parser."""

from datetime import date
from datetime import time as dt_time

from src.core.schedule_parser import (
    ParsedGroupSchedule,
    ParsedLesson,
    ParsedSchedule,
)
from src.models.enums import EducationLevel, LessonType


class TestParsedLesson:
    """Tests for ParsedLesson named tuple."""

    def test_parsed_lesson_creation(self) -> None:
        """Test creating ParsedLesson."""
        lesson = ParsedLesson(
            subject="Анатомия",
            lesson_type=LessonType.LECTURE,
            date=date(2024, 9, 1),
            start_time=dt_time(9, 0),
            end_time=dt_time(10, 30),
            teacher="Иванов И.И.",
            address="Кафедра анатомии",
            room="101",
        )
        assert lesson.subject == "Анатомия"
        assert lesson.lesson_type == LessonType.LECTURE
        assert lesson.teacher == "Иванов И.И."

    def test_parsed_lesson_optional_fields(self) -> None:
        """Test ParsedLesson with optional None fields."""
        lesson = ParsedLesson(
            subject="Анатомия",
            lesson_type=LessonType.LECTURE,
            date=date(2024, 9, 1),
            start_time=dt_time(9, 0),
            end_time=dt_time(10, 30),
            teacher=None,
            address=None,
            room=None,
        )
        assert lesson.teacher is None
        assert lesson.address is None
        assert lesson.room is None


class TestParsedGroupSchedule:
    """Tests for ParsedGroupSchedule named tuple."""

    def test_parsed_group_schedule_creation(self) -> None:
        """Test creating ParsedGroupSchedule."""
        lessons = [
            ParsedLesson(
                subject="Анатомия",
                lesson_type=LessonType.LECTURE,
                date=date(2024, 9, 1),
                start_time=dt_time(9, 0),
                end_time=dt_time(10, 30),
                teacher="Иванов И.И.",
                address="Кафедра анатомии",
                room="101",
            )
        ]
        group = ParsedGroupSchedule(
            speciality_code="31.05.01",
            speciality_full_name="31.05.01 Лечебное дело",
            speciality_clean_name="Лечебное дело",
            speciality_level=EducationLevel.SPECIALIST,
            course_number=1,
            stream="ОМ",
            group_name="ЛД-01",
            subgroup_name="1п",
            lessons=lessons,
        )
        assert group.speciality_code == "31.05.01"
        assert group.course_number == 1
        assert len(group.lessons) == 1

    def test_parsed_group_schedule_empty_lessons(self) -> None:
        """Test ParsedGroupSchedule with empty lessons list."""
        group = ParsedGroupSchedule(
            speciality_code="31.05.01",
            speciality_full_name="31.05.01 Лечебное дело",
            speciality_clean_name="Лечебное дело",
            speciality_level=EducationLevel.SPECIALIST,
            course_number=1,
            stream="ОМ",
            group_name="ЛД-01",
            subgroup_name="1п",
            lessons=[],
        )
        assert len(group.lessons) == 0


class TestParsedSchedule:
    """Tests for ParsedSchedule named tuple."""

    def test_parsed_schedule_creation(self) -> None:
        """Test creating ParsedSchedule."""
        lessons = [
            ParsedLesson(
                subject="Анатомия",
                lesson_type=LessonType.LECTURE,
                date=date(2024, 9, 1),
                start_time=dt_time(9, 0),
                end_time=dt_time(10, 30),
                teacher="Иванов И.И.",
                address="Кафедра анатомии",
                room="101",
            )
        ]
        group = ParsedGroupSchedule(
            speciality_code="31.05.01",
            speciality_full_name="31.05.01 Лечебное дело",
            speciality_clean_name="Лечебное дело",
            speciality_level=EducationLevel.SPECIALIST,
            course_number=1,
            stream="ОМ",
            group_name="ЛД-01",
            subgroup_name="1п",
            lessons=lessons,
        )
        schedule = ParsedSchedule(groups=[group])
        assert len(schedule.groups) == 1
        assert schedule.groups[0].speciality_code == "31.05.01"

    def test_parsed_schedule_empty_groups(self) -> None:
        """Test ParsedSchedule with empty groups."""
        schedule = ParsedSchedule(groups=[])
        assert len(schedule.groups) == 0

    def test_parsed_schedule_multiple_groups(self) -> None:
        """Test ParsedSchedule with multiple groups."""
        groups = []
        for i in range(3):
            group = ParsedGroupSchedule(
                speciality_code=f"31.05.0{i + 1}",
                speciality_full_name=f"31.05.0{i + 1} Speciality",
                speciality_clean_name=f"Speciality {i + 1}",
                speciality_level=EducationLevel.SPECIALIST,
                course_number=i + 1,
                stream="ОМ",
                group_name=f"Group-{i + 1:02d}",
                subgroup_name="1п",
                lessons=[],
            )
            groups.append(group)

        schedule = ParsedSchedule(groups=groups)
        assert len(schedule.groups) == 3
