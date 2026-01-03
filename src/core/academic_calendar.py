import datetime
from enum import IntEnum, StrEnum


class WeekDay(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class WeekDayShort(StrEnum):
    MON = "пн"
    TUE = "вт"
    WED = "ср"
    THU = "чт"
    FRI = "пт"
    SAT = "сб"
    SUN = "вс"


class Semester(IntEnum):
    FALL = 1
    SPRING = 2


DAY_NAME_MAP = {
    "пн": WeekDay.MONDAY,
    "вт": WeekDay.TUESDAY,
    "ср": WeekDay.WEDNESDAY,
    "чт": WeekDay.THURSDAY,
    "пт": WeekDay.FRIDAY,
    "сб": WeekDay.SATURDAY,
    "вс": WeekDay.SUNDAY,
}


def calculate_semester_start_date(
    year_start: int, year_end: int, semester_type: str
) -> datetime.date:
    """
    Calculate the semester start date based on the academic calendar.
    """
    semester_type_lower = semester_type.lower()

    if "осен" in semester_type_lower:
        start_date = datetime.date(year_start, 9, 1)
    else:
        start_date = datetime.date(year_end, 2, 10)

    if start_date.weekday() == WeekDay.SUNDAY:
        start_date += datetime.timedelta(days=1)

    return start_date


def parse_academic_year(academic_year: str) -> tuple[int, int]:
    """
    Parse academic year string like "2024/2025" into (2024, 2025).
    """
    year_start, year_end = map(int, academic_year.split("/"))
    return year_start, year_end


def calculate_lesson_date(
    semester_start: datetime.date,
    week_number: int,
    day_name: str,
) -> datetime.date:
    """
    Calculate exact date for lesson based on semester start, week number and day name.

    Args:
        semester_start: First day of semester
        week_number: Week number in semester (1-based)
        day_name: Day name in Russian ("пн", "вт", etc.)

    Returns:
        Exact date of the lesson
    """
    week_offset = week_number - 1
    target_day_index = DAY_NAME_MAP.get(day_name.lower(), WeekDay.MONDAY)
    return semester_start + datetime.timedelta(weeks=week_offset, days=target_day_index.value)


def parse_time_string(time_str: str) -> tuple[datetime.time, datetime.time]:
    """
    Parse time string like "09.00-10.30" into start_time and end_time.
    """
    time_str = time_str.replace(":", ".")
    start_str, end_str = time_str.split("-")

    start_hour, start_minute = map(int, start_str.split("."))
    end_hour, end_minute = map(int, end_str.split("."))

    start_time = datetime.time(start_hour, start_minute)
    end_time = datetime.time(end_hour, end_minute)

    return start_time, end_time


def get_semester_week_dates(
    semester_start: datetime.date,
    week_number: int,
) -> tuple[datetime.date, datetime.date]:
    """
    Get start and end dates of a specific week in semester.
    """
    week_start = semester_start + datetime.timedelta(weeks=week_number - 1)
    week_end = week_start + datetime.timedelta(days=6)

    return week_start, week_end
