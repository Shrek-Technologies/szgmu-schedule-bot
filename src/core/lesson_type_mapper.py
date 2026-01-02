from models import LessonType


def parse_lesson_type(raw: str | None) -> LessonType:
    """Parse lesson type string to LessonType enum.

    Args:
        raw: Raw lesson type string from API

    Returns:
        LessonType.LECTURE or LessonType.SEMINAR
    """
    if not raw:
        return LessonType.LECTURE

    value = raw.lower()
    if "семинар" in value:
        return LessonType.SEMINAR

    return LessonType.LECTURE
