import datetime
import pytest

from src.core.academic_calendar import (
    WeekDay,
    Semester,
    calculate_semester_start_date,
    parse_academic_year,
    calculate_lesson_date,
    parse_time_string,
    get_semester_week_dates,
    DAY_NAME_MAP,
)


class TestWeekDay:
    def test_weekday_values(self):
        """Тестируем значения перечисления WeekDay."""
        assert WeekDay.MONDAY == 0
        assert WeekDay.TUESDAY == 1
        assert WeekDay.WEDNESDAY == 2
        assert WeekDay.THURSDAY == 3
        assert WeekDay.FRIDAY == 4
        assert WeekDay.SATURDAY == 5
        assert WeekDay.SUNDAY == 6


class TestSemester:
    def test_semester_values(self):
        """Тестируем значения перечисления Semester."""
        assert Semester.FALL == 1
        assert Semester.SPRING == 2


class TestDayNameMap:
    def test_day_name_map(self):
        """Тестируем маппинг русских сокращений дней недели."""
        assert DAY_NAME_MAP["пн"] == WeekDay.MONDAY
        assert DAY_NAME_MAP["вт"] == WeekDay.TUESDAY
        assert DAY_NAME_MAP["ср"] == WeekDay.WEDNESDAY
        assert DAY_NAME_MAP["чт"] == WeekDay.THURSDAY
        assert DAY_NAME_MAP["пт"] == WeekDay.FRIDAY
        assert DAY_NAME_MAP["сб"] == WeekDay.SATURDAY
        assert DAY_NAME_MAP["вс"] == WeekDay.SUNDAY


class TestCalculateSemesterStartDate:
    @pytest.mark.parametrize(
        "year_start,year_end,semester_type,expected_date",
        [
            # 1 сентября 2024 - это воскресенье, поэтому смещаем на 2 сентября
            (2024, 2025, "Осенний", datetime.date(2024, 9, 2)),
            (2024, 2025, "осенний", datetime.date(2024, 9, 2)),
            (2024, 2025, "Осень", datetime.date(2024, 9, 2)),
            (2023, 2024, "Весенний", datetime.date(2024, 2, 10)),
            (2023, 2024, "весенний", datetime.date(2024, 2, 10)),
            (2023, 2024, "Весна", datetime.date(2024, 2, 10)),
            # 10 февраля 2025 - это понедельник, без смещения
            (2024, 2025, "весенний", datetime.date(2025, 2, 10)),
        ]
    )
    def test_semester_start_date(self, year_start, year_end, semester_type, expected_date):
        """Тестируем расчет даты начала семестра."""
        result = calculate_semester_start_date(year_start, year_end, semester_type)
        assert result == expected_date

    def test_fall_semester_start_on_sunday(self):
        """Тестируем случай, когда осенний семестр начинается в воскресенье."""
        # 1 сентября 2024 - это воскресенье
        result = calculate_semester_start_date(2024, 2025, "осенний")
        assert result == datetime.date(2024, 9, 2)  # Смещаем на понедельник

    def test_spring_semester_start_on_sunday(self):
        """Тестируем случай, когда весенний семестр начинается в воскресенье."""
        # 10 февраля 2030 - это воскресенье
        result = calculate_semester_start_date(2029, 2030, "весенний")
        assert result == datetime.date(2030, 2, 11)  # Смещаем на понедельник


class TestParseAcademicYear:
    @pytest.mark.parametrize(
        "academic_year,expected_result",
        [
            ("2024/2025", (2024, 2025)),
            ("2023/2024", (2023, 2024)),
            ("2025/2026", (2025, 2026)),
        ]
    )
    def test_parse_academic_year_valid(self, academic_year, expected_result):
        """Тестируем парсинг корректных строк учебного года."""
        result = parse_academic_year(academic_year)
        assert result == expected_result

    def test_parse_academic_year_invalid_format(self):
        """Тестируем парсинг некорректного формата."""
        with pytest.raises(ValueError):
            parse_academic_year("2024-2025")

    def test_parse_academic_year_not_numbers(self):
        """Тестируем парсинг строки не с числами."""
        with pytest.raises(ValueError):
            parse_academic_year("abc/def")


class TestCalculateLessonDate:
    def test_calculate_lesson_date_basic(self):
        """Тестируем базовый расчет даты занятия."""
        semester_start = datetime.date(2024, 9, 2)  # Понедельник (1.09 было воскресенье)
        week_number = 3
        day_name = "ср"  # Среда

        result = calculate_lesson_date(semester_start, week_number, day_name)
        # Семестр начался 2.09 (понедельник)
        # 3 неделя: 16-22 сентября, среда = 18 сентября
        expected = datetime.date(2024, 9, 18)
        assert result == expected

    @pytest.mark.parametrize(
        "day_name,expected_weekday",
        [
            ("пн", WeekDay.MONDAY),
            ("вт", WeekDay.TUESDAY),
            ("ср", WeekDay.WEDNESDAY),
            ("чт", WeekDay.THURSDAY),
            ("пт", WeekDay.FRIDAY),
            ("сб", WeekDay.SATURDAY),
            ("вс", WeekDay.SUNDAY),
        ]
    )
    def test_all_days_calculation(self, day_name, expected_weekday):
        """Тестируем расчет для всех дней недели."""
        semester_start = datetime.date(2024, 2, 12)  # Понедельник
        week_number = 1

        result = calculate_lesson_date(semester_start, week_number, day_name)
        assert result.weekday() == expected_weekday.value

    def test_first_week_calculation(self):
        """Тестируем расчет для первой недели."""
        semester_start = datetime.date(2024, 9, 2)  # Понедельник
        week_number = 1
        day_name = "пн"

        result = calculate_lesson_date(semester_start, week_number, day_name)
        assert result == semester_start

    def test_unknown_day_name_fallback(self):
        """Тестируем расчет с неизвестным названием дня (должен вернуть понедельник)."""
        semester_start = datetime.date(2024, 9, 2)
        week_number = 1
        day_name = "xyz"  # Неизвестное название

        result = calculate_lesson_date(semester_start, week_number, day_name)
        assert result == semester_start  # Должен вернуть понедельник

    def test_calculate_with_sunday_start(self): ######################################################
        """Тестируем расчет, когда семестр начинается во вторник."""
        semester_start = datetime.date(2024, 9, 2)
        week_number = 1
        day_name = "вт"

        result = calculate_lesson_date(semester_start, week_number, day_name)
        assert result == datetime.date(2024, 9, 3)


class TestParseTimeString:
    @pytest.mark.parametrize(
        "time_str,expected_start,expected_end",
        [
            ("09.00-10.30", datetime.time(9, 0), datetime.time(10, 30)),
            ("09:00-10:30", datetime.time(9, 0), datetime.time(10, 30)),
            ("13.15-14.45", datetime.time(13, 15), datetime.time(14, 45)),
            ("18.30-20.00", datetime.time(18, 30), datetime.time(20, 0)),
        ]
    )
    def test_parse_time_string(self, time_str, expected_start, expected_end):
        """Тестируем парсинг строки времени."""
        start_time, end_time = parse_time_string(time_str)
        assert start_time == expected_start
        assert end_time == expected_end

    def test_parse_time_string_invalid_format(self):
        """Тестируем парсинг некорректного формата времени."""
        with pytest.raises(ValueError):
            parse_time_string("09.00")

    def test_parse_time_string_wrong_separator(self):
        """Тестируем парсинг времени с неправильным разделителем."""
        with pytest.raises(ValueError):
            parse_time_string("09.00/10.30")


class TestGetSemesterWeekDates:
    def test_get_semester_week_dates_first_week(self):
        """Тестируем получение дат первой недели."""
        semester_start = datetime.date(2024, 9, 2)
        week_start, week_end = get_semester_week_dates(semester_start, 1)

        assert week_start == datetime.date(2024, 9, 2)
        assert week_end == datetime.date(2024, 9, 8)

    def test_get_semester_week_dates_third_week(self):
        """Тестируем получение дат третьей недели."""
        semester_start = datetime.date(2024, 9, 2)
        week_start, week_end = get_semester_week_dates(semester_start, 3)

        assert week_start == datetime.date(2024, 9, 16)
        assert week_end == datetime.date(2024, 9, 22)

    def test_get_semester_week_dates_with_sunday_start(self):
        """Тестируем получение дат недели, когда семестр начинается в воскресенье."""
        semester_start = datetime.date(2024, 9, 1)  # Воскресенье
        week_start, week_end = get_semester_week_dates(semester_start, 1)

        assert week_start == datetime.date(2024, 9, 1)
        assert week_end == datetime.date(2024, 9, 7)