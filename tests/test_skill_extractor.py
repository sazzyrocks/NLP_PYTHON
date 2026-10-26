"""Unit tests for skill extractor."""

from pathlib import Path
import pytest

from src.skill_extractor import SkillExtractor, get_skill_extractor


@pytest.fixture(scope="module")
def extractor():
    """Module-level SkillExtractor instance."""
    return get_skill_extractor()


def test_extract_skills_canonical_and_aliases(extractor):
    """Verify canonical naming and alias mapping."""
    text = "Proficient in js, golang, postgres, and k8s."
    skills = extractor.extract_skills(text)

    assert "JavaScript" in skills
    assert "Go" in skills
    assert "PostgreSQL" in skills
    assert "Kubernetes" in skills


def test_extract_skills_java_vs_javascript(extractor):
    """Critical check: Java must NOT match inside JavaScript or vice versa."""
    js_only = "Expert in JavaScript web development."
    skills_js = extractor.extract_skills(js_only)
    assert "JavaScript" in skills_js
    assert "Java" not in skills_js

    java_only = "Backend engineering in Java enterprise systems."
    skills_java = extractor.extract_skills(java_only)
    assert "Java" in skills_java
    assert "JavaScript" not in skills_java

    both = "Full stack developer using both Java and JavaScript."
    skills_both = extractor.extract_skills(both)
    assert "Java" in skills_both
    assert "JavaScript" in skills_both


def test_extract_skills_technical_symbols(extractor):
    """Verify c++, c#, .net, node.js extraction."""
    text = "Building services with C++, C#, .NET, and Node.js."
    skills = extractor.extract_skills(text)
    assert "C++" in skills
    assert "C#" in skills
    assert ".NET" in skills
    assert "Node.js" in skills


def test_extract_skills_deduplication_and_sorting(extractor):
    """Verify duplicate mentions are deduplicated and sorted."""
    text = "Python developer. Python backend. Python scripting with python3 and py."
    skills = extractor.extract_skills(text)
    assert skills.count("Python") == 1
    assert skills == ["Python"]


def test_extract_skills_empty(extractor):
    """Verify empty or non-matching string returns empty list."""
    assert extractor.extract_skills("") == []
    assert extractor.extract_skills("No technical skills are mentioned in this sentence.") == []


def test_group_skills_by_category(extractor):
    """Verify skill categorization."""
    skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Communication"]
    grouped = extractor.group_skills_by_category(skills)

    assert "Python" in grouped.get("languages", [])
    assert "FastAPI" in grouped.get("frameworks", [])
    assert "PostgreSQL" in grouped.get("databases", [])
    assert "Docker" in grouped.get("devops", [])
    assert "AWS" in grouped.get("cloud", [])
    assert "Communication" in grouped.get("soft_skills", [])


def test_invalid_taxonomy_path():
    """Verify missing taxonomy file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        SkillExtractor(skills_json_path=Path("non_existent_taxonomy_file.json"))
