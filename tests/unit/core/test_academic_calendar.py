"""Unit tests for core academic calendar utilities."""

from datetime import date
from datetime import time as dt_time

from src.core.academic_calendar import (
    DAY_NAME_MAP,
    WeekDay,
    calculate_lesson_date,
    calculate_semester_start_date,
    get_semester_week_dates,
    parse_academic_year,
    parse_time_string,
)


class TestWeekDay:
    """Tests for WeekDay enum."""

    def test_week_day_monday_is_zero(self) -> None:
        """Test Monday is 0."""
        assert WeekDay.MONDAY == 0

    def test_week_day_sunday_is_six(self) -> None:
        """Test Sunday is 6."""
        assert WeekDay.SUNDAY == 6

    def test_week_day_values_sequential(self) -> None:
        """Test weekday values are sequential."""
        assert WeekDay.TUESDAY == WeekDay.MONDAY + 1
        assert WeekDay.WEDNESDAY == WeekDay.TUESDAY + 1


class TestDayNameMap:
    """Tests for DAY_NAME_MAP constant."""

    def test_day_name_map_contains_all_days(self) -> None:
        """Test map contains all 7 days."""
        assert len(DAY_NAME_MAP) == 7

    def test_day_name_map_monday(self) -> None:
        """Test Monday mapping."""
        assert DAY_NAME_MAP["пн"] == WeekDay.MONDAY

    def test_day_name_map_sunday(self) -> None:
        """Test Sunday mapping."""
        assert DAY_NAME_MAP["вс"] == WeekDay.SUNDAY


class TestCalculateSemesterStartDate:
    """Tests for calculate_semester_start_date function."""

    def test_fall_semester_starts_september_first(self) -> None:
        """Test fall semester starts on Sept 1."""
        result = calculate_semester_start_date(2024, 2025, "осеннего")
        assert result.month == 9
        assert result.day >= 1

    def test_spring_semester_starts_february(self) -> None:
        """Test spring semester starts in February."""
        result = calculate_semester_start_date(2024, 2025, "весеннего")
        assert result.month == 2

    def test_semester_start_not_on_sunday(self) -> None:
        """Test semester start is never on Sunday."""
        result = calculate_semester_start_date(2024, 2025, "осеннего")
        assert result.weekday() != WeekDay.SUNDAY

    def test_different_years_produce_different_dates(self) -> None:
        """Test different years produce different dates."""
        result1 = calculate_semester_start_date(2023, 2024, "осеннего")
        result2 = calculate_semester_start_date(2024, 2025, "осеннего")
        assert result1.year != result2.year


class TestParseAcademicYear:
    """Tests for parse_academic_year function."""

    def test_parse_academic_year_2024_2025(self) -> None:
        """Test parsing 2024/2025."""
        year_start, year_end = parse_academic_year("2024/2025")
        assert year_start == 2024
        assert year_end == 2025

    def test_parse_academic_year_2023_2024(self) -> None:
        """Test parsing 2023/2024."""
        year_start, year_end = parse_academic_year("2023/2024")
        assert year_start == 2023
        assert year_end == 2024

    def test_parse_academic_year_returns_tuple_of_ints(self) -> None:
        """Test return type is tuple of ints."""
        result = parse_academic_year("2024/2025")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)


class TestCalculateLessonDate:
    """Tests for calculate_lesson_date function."""

    def test_calculate_lesson_date_first_week_monday(self) -> None:
        """Test lesson date for first week, Monday."""
        semester_start = date(2024, 9, 2)
        result = calculate_lesson_date(semester_start, 1, "пн")
        assert result.weekday() == WeekDay.MONDAY

    def test_calculate_lesson_date_second_week(self) -> None:
        """Test lesson date for second week."""
        semester_start = date(2024, 9, 2)
        first_week = calculate_lesson_date(semester_start, 1, "пн")
        second_week = calculate_lesson_date(semester_start, 2, "пн")
        assert (second_week - first_week).days == 7

    def test_calculate_lesson_date_different_days(self) -> None:
        """Test different days of same week."""
        semester_start = date(2024, 9, 2)
        monday = calculate_lesson_date(semester_start, 1, "пн")
        tuesday = calculate_lesson_date(semester_start, 1, "вт")
        assert (tuesday - monday).days == 1

    def test_calculate_lesson_date_friday(self) -> None:
        """Test Friday lesson date."""
        semester_start = date(2024, 9, 2)
        result = calculate_lesson_date(semester_start, 1, "пт")
        assert result.weekday() == WeekDay.FRIDAY


class TestParseTimeString:
    """Tests for parse_time_string function."""

    def test_parse_time_string_simple(self) -> None:
        """Test parsing simple time string."""
        start, end = parse_time_string("09.00-10.30")
        assert start == dt_time(9, 0)
        assert end == dt_time(10, 30)

    def test_parse_time_string_afternoon(self) -> None:
        """Test parsing afternoon time string."""
        start, end = parse_time_string("14.30-16.00")
        assert start == dt_time(14, 30)
        assert end == dt_time(16, 0)

    def test_parse_time_string_with_colons(self) -> None:
        """Test parsing time string with colons (alternative format)."""
        start, end = parse_time_string("09:00-10:30")
        assert start == dt_time(9, 0)
        assert end == dt_time(10, 30)

    def test_parse_time_string_returns_time_objects(self) -> None:
        """Test return values are time objects."""
        start, end = parse_time_string("09.00-10.30")
        assert isinstance(start, dt_time)
        assert isinstance(end, dt_time)

    def test_parse_time_string_start_before_end(self) -> None:
        """Test start time is before end time."""
        start, end = parse_time_string("09.00-10.30")
        assert start < end


class TestGetSemesterWeekDates:
    """Tests for get_semester_week_dates function."""

    def test_get_semester_week_dates_first_week(self) -> None:
        """Test first week dates."""
        semester_start = date(2024, 9, 2)
        start, end = get_semester_week_dates(semester_start, 1)
        assert start == semester_start
        assert (end - start).days == 6

    def test_get_semester_week_dates_second_week(self) -> None:
        """Test second week dates."""
        semester_start = date(2024, 9, 2)
        start, end = get_semester_week_dates(semester_start, 2)
        first_start, _ = get_semester_week_dates(semester_start, 1)
        assert (start - first_start).days == 7

    def test_get_semester_week_dates_returns_seven_day_span(self) -> None:
        """Test week span is always 7 days."""
        semester_start = date(2024, 9, 2)
        for week in range(1, 5):
            start, end = get_semester_week_dates(semester_start, week)
            assert (end - start).days == 6
