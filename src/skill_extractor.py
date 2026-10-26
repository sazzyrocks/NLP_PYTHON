"""Skill extraction module using spaCy PhraseMatcher and taxonomy-driven alias mapping."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
import spacy
from spacy.matcher import PhraseMatcher


class SkillExtractor:
    """Extracts standardized skills from text using spaCy's PhraseMatcher.

    Matches skill names and aliases with token boundary enforcement,
    preventing substring collisions (e.g., 'Java' matching inside 'JavaScript').
    """

    def __init__(self, skills_json_path: Optional[Path] = None):
        """Initialize the SkillExtractor with a taxonomy JSON file.

        Args:
            skills_json_path: Path to skills.json. Defaults to data/skills.json.
        """
        if skills_json_path is None:
            base_dir = Path(__file__).resolve().parent.parent
            skills_json_path = base_dir / "data" / "skills.json"

        self.skills_json_path = Path(skills_json_path)
        self.taxonomy: Dict[str, List[Dict[str, any]]] = self._load_taxonomy()
        self.canonical_to_category: Dict[str, str] = {}
        self.all_canonical_skills: Set[str] = set()

        # Initialize spaCy
        self.nlp = self._init_spacy()
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self._build_matcher()

    def _init_spacy(self) -> spacy.language.Language:
        """Initialize spaCy English model or fallback to blank English model."""
        try:
            return spacy.load("en_core_web_sm", exclude=["ner", "parser", "tagger", "lemmatizer"])
        except Exception:
            return spacy.blank("en")

    def _load_taxonomy(self) -> Dict[str, List[Dict[str, any]]]:
        """Load skill taxonomy from the specified JSON path."""
        if not self.skills_json_path.exists():
            raise FileNotFoundError(f"Skills taxonomy file not found: {self.skills_json_path}")

        with open(self.skills_json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_matcher(self) -> None:
        """Register all skills and their aliases in the PhraseMatcher."""
        for category, skill_list in self.taxonomy.items():
            for item in skill_list:
                canonical = item["name"]
                self.all_canonical_skills.add(canonical)
                self.canonical_to_category[canonical] = category

                aliases = set(item.get("aliases", []))
                aliases.add(canonical.lower())

                patterns = []
                for alias in aliases:
                    cleaned_alias = alias.strip().lower()
                    if cleaned_alias:
                        # make_doc is fast tokenization without pipeline components
                        patterns.append(self.nlp.make_doc(cleaned_alias))

                if patterns:
                    self.matcher.add(canonical, patterns)

    def extract_skills(self, text: str) -> List[str]:
        """Extract canonical skill names from text.

        Args:
            text: Input resume or job description text.

        Returns:
            Sorted, deduplicated list of canonical skill names found in the text.
        """
        if not text or not text.strip():
            return []

        doc = self.nlp.make_doc(text)
        matches = self.matcher(doc)

        matched_skills: Set[str] = set()
        for match_id, _start, _end in matches:
            canonical_name = self.nlp.vocab.strings[match_id]
            matched_skills.add(canonical_name)

        return sorted(list(matched_skills))

    def get_category_for_skill(self, skill_name: str) -> str:
        """Return the category for a given canonical skill name."""
        return self.canonical_to_category.get(skill_name, "other")

    def group_skills_by_category(self, skills: List[str]) -> Dict[str, List[str]]:
        """Group a list of canonical skills by their taxonomy category.

        Args:
            skills: List of canonical skill names.

        Returns:
            Dictionary mapping category name to list of skills in that category.
        """
        grouped: Dict[str, List[str]] = {}
        for skill in skills:
            cat = self.get_category_for_skill(skill)
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(skill)

        for cat in grouped:
            grouped[cat] = sorted(grouped[cat])
        return grouped


# Global instance cache for efficiency
_DEFAULT_EXTRACTOR: Optional[SkillExtractor] = None


def get_skill_extractor() -> SkillExtractor:
    """Retrieve or initialize the singleton SkillExtractor instance."""
    global _DEFAULT_EXTRACTOR
    if _DEFAULT_EXTRACTOR is None:
        _DEFAULT_EXTRACTOR = SkillExtractor()
    return _DEFAULT_EXTRACTOR
