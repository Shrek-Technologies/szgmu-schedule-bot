import datetime
import logging
from typing import NamedTuple

from api.schemas.responses import ScheduleLesson, XlsxScheduleDetail
from core.academic_calendar import (
    calculate_lesson_date,
    calculate_semester_start_date,
    parse_academic_year,
    parse_time_string,
)
from core.lesson_type_mapper import parse_lesson_type
from core.speciality_parser import parse_speciality
from models import EducationLevel, LessonType

logger = logging.getLogger(__name__)


class ParsedLesson(NamedTuple):
    """Parsed lesson data ready for insertion."""

    subject: str
    lesson_type: LessonType
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    teacher: str | None
    address: str | None
    room: str | None


class ParsedGroupSchedule(NamedTuple):
    """Parsed group schedule with all related entities."""

    speciality_code: str
    speciality_full_name: str
    speciality_clean_name: str
    speciality_level: EducationLevel | None
    course_number: int
    stream: str
    group_name: str
    subgroup_name: str
    lessons: list[ParsedLesson]


class ParsedSchedule(NamedTuple):
    """Complete parsed schedule."""

    groups: list[ParsedGroupSchedule]


class ScheduleParser:
    """Pure parser for schedule data - no database access."""

    @staticmethod
    def parse(schedule_detail: XlsxScheduleDetail) -> ParsedSchedule:
        if not schedule_detail.schedule_lesson_dto_list:
            return ParsedSchedule(groups=[])

        if not schedule_detail.xlsx_header_dto:
            raise ValueError("Schedule has no header information")

        header = schedule_detail.xlsx_header_dto[0]
        year_start, year_end = parse_academic_year(header.academic_year)
        semester_start = calculate_semester_start_date(year_start, year_end, header.semester_type)

        # Group lessons by normalized key: use parsed speciality code and normalized strings
        groups_map: dict[tuple[str, int, str, str, str], list[ScheduleLesson]] = {}
        for lesson_dto in schedule_detail.schedule_lesson_dto_list:
            try:
                course_number = int(lesson_dto.course_number)
            except (ValueError, TypeError) as e:
                raise ValueError(f"invalid course number: {lesson_dto.course_number}") from e

            speciality = (lesson_dto.speciality or "").strip()
            stream = (lesson_dto.group_stream or "").strip()
            group_name = (lesson_dto.study_group or "").strip()
            subgroup_raw = (lesson_dto.subgroup or "").strip()
            subgroup_name = subgroup_raw.upper() if subgroup_raw else f"{group_name}A"

            group_key = (speciality, course_number, stream, group_name, subgroup_name)

            groups_map.setdefault(group_key, []).append(lesson_dto)

        parsed_groups = []
        for (
            speciality,
            course_number,
            stream,
            group_name,
            subgroup_name,
        ), lesson_dtos in groups_map.items():
            parsed_group = ScheduleParser._parse_group(
                speciality,
                lesson_dtos,
                semester_start,
                course_number=course_number,
                stream=stream,
                group_name=group_name,
                subgroup_name=subgroup_name,
            )
            parsed_groups.append(parsed_group)

        return ParsedSchedule(groups=parsed_groups)

    @staticmethod
    def _parse_group(
        speciality: str,
        lesson_dtos: list[ScheduleLesson],
        semester_start: datetime.date,
        *,
        course_number: int,
        stream: str,
        group_name: str,
        subgroup_name: str,
    ) -> ParsedGroupSchedule:
        parsed_spec = parse_speciality(speciality)

        # Build lessons dict to deduplicate by (date, start_time, subject)
        lessons_map: dict[tuple[datetime.date, datetime.time, str], ParsedLesson] = {}

        for lesson_dto in lesson_dtos:
            try:
                parsed_lesson = ScheduleParser._parse_lesson(lesson_dto, semester_start)
            except Exception as e:
                # Skip bad lessons but log them
                logger.warning(
                    "Skipping lesson due parse error: %s -> %s",
                    getattr(lesson_dto, "subject_name", "<unknown>"),
                    e,
                )
                continue

            # Deduplication key: date + start_time + normalized subject
            key = (
                parsed_lesson.date,
                parsed_lesson.start_time,
                parsed_lesson.subject.strip().casefold(),
            )
            # "last write wins" — if duplicates appear, newer DTO overwrites older
            lessons_map[key] = parsed_lesson

        return ParsedGroupSchedule(
            speciality_code=parsed_spec.code,
            speciality_full_name=speciality,
            speciality_clean_name=parsed_spec.clean_name,
            speciality_level=parsed_spec.level,
            course_number=course_number,
            stream=stream,
            group_name=group_name,
            subgroup_name=subgroup_name,
            lessons=list(lessons_map.values()),
        )

    @staticmethod
    def _parse_lesson(lesson_dto: ScheduleLesson, semester_start: datetime.date) -> ParsedLesson:
        try:
            week_number = int(lesson_dto.week_number)
        except (ValueError, TypeError) as e:
            raise ValueError(f"invalid week number: {lesson_dto.week_number}") from e

        lesson_date = calculate_lesson_date(semester_start, week_number, lesson_dto.day_name)
        start_time, end_time = parse_time_string(lesson_dto.pair_time)
        lesson_type = parse_lesson_type(lesson_dto.lesson_type)

        return ParsedLesson(
            subject=(lesson_dto.subject_name or "").strip(),
            lesson_type=lesson_type,
            date=lesson_date,
            start_time=start_time,
            end_time=end_time,
            teacher=(lesson_dto.lector_name or "").strip() or None,
            address=(lesson_dto.location_address or "").strip() or None,
            room=(lesson_dto.auditory_number or "").strip() or None,
        )
