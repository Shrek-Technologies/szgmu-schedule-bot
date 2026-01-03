"""Unit tests for lesson type mapper."""

from src.core.lesson_type_mapper import parse_lesson_type
from src.models.enums import LessonType


class TestParseLessonType:
    """Tests for parse_lesson_type function."""

    def test_parse_lesson_type_none_defaults_to_lecture(self) -> None:
        """Test None input returns LECTURE."""
        result = parse_lesson_type(None)
        assert result == LessonType.LECTURE

    def test_parse_lesson_type_empty_string_defaults_to_lecture(self) -> None:
        """Test empty string returns LECTURE."""
        result = parse_lesson_type("")
        assert result == LessonType.LECTURE

    def test_parse_lesson_type_seminar_russian(self) -> None:
        """Test Russian word 'семинар' returns SEMINAR."""
        result = parse_lesson_type("семинарского занятия")
        assert result == LessonType.SEMINAR

    def test_parse_lesson_type_seminar_uppercase(self) -> None:
        """Test uppercase Russian word 'СЕМИНАР' returns SEMINAR."""
        result = parse_lesson_type("СЕМИНАРСКОГО ЗАНЯТИЯ")
        assert result == LessonType.SEMINAR

    def test_parse_lesson_type_lecture_russian(self) -> None:
        """Test Russian word 'лекция' returns LECTURE."""
        result = parse_lesson_type("лекционного занятия")
        assert result == LessonType.LECTURE

    def test_parse_lesson_type_lecture_default(self) -> None:
        """Test unknown text defaults to LECTURE."""
        result = parse_lesson_type("практическое занятие")
        assert result == LessonType.LECTURE

    def test_parse_lesson_type_case_insensitive(self) -> None:
        """Test parsing is case-insensitive."""
        result_lower = parse_lesson_type("семинар")
        result_upper = parse_lesson_type("СЕМИНАР")
        assert result_lower == result_upper == LessonType.SEMINAR
