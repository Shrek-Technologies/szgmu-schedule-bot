from enum import StrEnum


class LessonType(StrEnum):
    LECTURE = "лекционного"
    SEMINAR = "семинарского"


class EducationLevel(StrEnum):
    BACHELOR = "bachelor"
    SPECIALIST = "specialist"
    MASTER = "master"
    RESIDENCY = "residency"
