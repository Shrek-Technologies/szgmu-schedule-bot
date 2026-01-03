"""Unit tests for speciality parser."""

from src.core.speciality_parser import (
    ParsedSpeciality,
    extract_education_level,
    parse_speciality,
)
from src.models.enums import EducationLevel


class TestExtractEducationLevel:
    """Tests for extract_education_level function."""

    def test_extract_education_level_master(self) -> None:
        """Test extracting MASTER level."""
        result = extract_education_level("программа магистратуры")
        assert result == EducationLevel.MASTER

    def test_extract_education_level_specialist(self) -> None:
        """Test extracting SPECIALIST level."""
        result = extract_education_level("специалитет лечебное дело")
        assert result == EducationLevel.SPECIALIST

    def test_extract_education_level_bachelor(self) -> None:
        """Test extracting BACHELOR level."""
        result = extract_education_level("бакалавриат информатика")
        assert result == EducationLevel.BACHELOR

    def test_extract_education_level_residency(self) -> None:
        """Test extracting RESIDENCY level."""
        result = extract_education_level("ординатура по хирургии")
        assert result == EducationLevel.RESIDENCY

    def test_extract_education_level_residency_with_resident(self) -> None:
        """Test extracting RESIDENCY level with 'резидент'."""
        result = extract_education_level("резидент по кардиологии")
        assert result == EducationLevel.RESIDENCY

    def test_extract_education_level_unknown_defaults_to_bachelor(self) -> None:
        """Test unknown level defaults to BACHELOR."""
        result = extract_education_level("программа подготовки")
        assert result == EducationLevel.BACHELOR

    def test_extract_education_level_case_insensitive(self) -> None:
        """Test extraction is case-insensitive."""
        result1 = extract_education_level("магистратура")
        result2 = extract_education_level("МАГИСТРАТУРА")
        assert result1 == result2 == EducationLevel.MASTER

    def test_extract_education_level_magister_synonym(self) -> None:
        """Test 'магистр' is recognized."""
        result = extract_education_level("магистр информационных систем")
        assert result == EducationLevel.MASTER


class TestParseSpeciality:
    """Tests for parse_speciality function."""

    def test_parse_speciality_full_example(self) -> None:
        """Test parsing full speciality string."""
        full_name = "31.05.01 лечебное дело (специалитет)"
        result = parse_speciality(full_name)

        assert result.code == "31.05.01"
        assert "лечебное дело" in result.clean_name
        assert result.level == EducationLevel.SPECIALIST

    def test_parse_speciality_master_example(self) -> None:
        """Test parsing master speciality."""
        full_name = "32.04.01 общественное здравоохранение уровень магистратуры"
        result = parse_speciality(full_name)

        assert result.code == "32.04.01"
        assert "общественное здравоохранение" in result.clean_name
        assert result.level == EducationLevel.MASTER

    def test_parse_speciality_without_code(self) -> None:
        """Test parsing speciality without code."""
        full_name = "лечебное дело (специалитет)"
        result = parse_speciality(full_name)

        assert result.code == ""
        assert "лечебное дело" in result.clean_name
        assert result.level == EducationLevel.SPECIALIST

    def test_parse_speciality_returns_named_tuple(self) -> None:
        """Test return type is ParsedSpeciality NamedTuple."""
        result = parse_speciality("31.05.01 лечебное дело")
        assert isinstance(result, ParsedSpeciality)
        assert hasattr(result, "code")
        assert hasattr(result, "clean_name")
        assert hasattr(result, "level")

    def test_parse_speciality_code_extraction(self) -> None:
        """Test code extraction from various formats."""
        full_name = "32.05.01 стоматология (специалитет)"
        result = parse_speciality(full_name)
        assert result.code == "32.05.01"

    def test_parse_speciality_clean_name_no_level_indicators(self) -> None:
        """Test clean name has no level indicators."""
        full_name = "31.05.01 лечебное дело (специалитет)"
        result = parse_speciality(full_name)

        assert "специалитет" not in result.clean_name.lower()
        assert "магистратура" not in result.clean_name.lower()

    def test_parse_speciality_clean_name_no_extra_spaces(self) -> None:
        """Test clean name has no extra spaces."""
        full_name = "31.05.01    лечебное   дело   (специалитет)"
        result = parse_speciality(full_name)

        assert "  " not in result.clean_name
        assert len(result.clean_name.split()) > 0

    def test_parse_speciality_level_detection(self) -> None:
        """Test correct level detection."""
        tests = [
            ("31.05.01 лечебное дело (специалитет)", EducationLevel.SPECIALIST),
            ("32.04.01 эпидемиология (магистратура)", EducationLevel.MASTER),
            ("31.05.03 стоматология (бакалавр)", EducationLevel.BACHELOR),
        ]

        for full_name, expected_level in tests:
            result = parse_speciality(full_name)
            assert result.level == expected_level

    def test_parse_speciality_cleans_parentheses(self) -> None:
        """Test parentheses are cleaned from name."""
        full_name = "31.05.01 лечебное дело (специалитет)"
        result = parse_speciality(full_name)

        assert not result.clean_name.startswith("(")
        assert not result.clean_name.endswith(")")
