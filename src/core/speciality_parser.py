import re
from typing import NamedTuple

from models.enums import EducationLevel


class ParsedSpeciality(NamedTuple):
    """Result of parsing speciality string."""

    code: str
    clean_name: str
    level: EducationLevel | None


def extract_education_level(full_name: str) -> EducationLevel:
    """
    Extract education level from speciality full name.
    """
    full_name_lower = full_name.lower()

    if "магистр" in full_name_lower:
        return EducationLevel.MASTER
    elif "специалитет" in full_name_lower:
        return EducationLevel.SPECIALIST
    elif "бакалавр" in full_name_lower:
        return EducationLevel.BACHELOR
    elif "ординатура" in full_name_lower or "резидент" in full_name_lower:
        return EducationLevel.RESIDENCY
    else:
        return EducationLevel.BACHELOR


def parse_speciality(full_name: str) -> ParsedSpeciality:
    """
    Parse speciality full name into code, clean name and education level.

    Examples:
        "31.05.01 лечебное дело (специалитет)" ->
            code="31.05.01", clean_name="лечебное дело", level=SPECIALIST

        "32.04.01 общественное здравоохранение уровень магистратуры" ->
            code="32.04.01", clean_name="общественное здравоохранение", level=MASTER
    """
    # Extract code (assumes code is at the beginning)
    code_match = re.match(r"^(\d{2}\.\d{2}\.\d{2})\s+", full_name)
    code = code_match.group(1) if code_match else ""

    # Remove code from name
    name_without_code = full_name.replace(code, "").strip() if code else full_name

    # Extract education level
    level = extract_education_level(name_without_code)

    # Clean name - remove level indicators and extra information
    clean_name = name_without_code

    # Remove level indicators
    level_indicators = [
        "уровень магистратуры",
        "уровень специалитета",
        "уровень бакалавриата",
        "специалитет",
        "магистратуры",
        "магистр",
        "бакалавр",
        "ординатура",
        "резидент",
    ]

    for indicator in level_indicators:
        clean_name = clean_name.replace(indicator, "")

    # Remove form of study indicators
    form_indicators = [
        "форма обучения: очная",
        "форма обучения: очно-заочная",
        "форма обучения: заочная",
        "форма обучения:",
    ]

    for indicator in form_indicators:
        clean_name = clean_name.replace(indicator, "")

    # Clean extra punctuation and whitespace
    clean_name = re.sub(r"\s+", " ", clean_name)  # Multiple spaces to single
    clean_name = clean_name.strip(" ,-()")

    return ParsedSpeciality(
        code=code,
        clean_name=clean_name,
        level=level,
    )
