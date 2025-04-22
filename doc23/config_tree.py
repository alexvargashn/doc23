from dataclasses import dataclass, field
import re
from typing import Dict, Optional, Any
from typing_extensions import Self


@dataclass
class LevelConfig:
    """Configuration for a document level in the hierarchy.

    Attributes:
        pattern: Regex pattern to identify this level in the text.
        name: Unique level name (e.g., 'chapter', 'article').
        title_field: Field to store the title of this level.
        description_field: Optional field for description or content.
        sections_field: Optional field for sublevels.
        paragraph_field: Optional field for paragraph-level nodes or text.
        parent: Optional parent level name.
        is_leaf: If True, this level is considered terminal (won't contain sections).
    """
    pattern: str
    name: str
    title_field: str
    description_field: Optional[str] = None
    sections_field: Optional[str] = None
    paragraph_field: Optional[str] = None
    parent: Optional[str] = None
    is_leaf: bool = False

    def __post_init__(self):
        if not isinstance(self.pattern, str):
            raise ValueError("pattern must be a string")
        if not isinstance(self.name, str):
            raise ValueError("name must be a string")
        if not isinstance(self.title_field, str):
            raise ValueError("title_field must be a string")

        for attr_name in ["description_field", "sections_field", "paragraph_field", "parent"]:
            attr_value = getattr(self, attr_name)
            if attr_value is not None and not isinstance(attr_value, str):
                raise ValueError(f"{attr_name} must be a string or None")

        if not isinstance(self.is_leaf, bool):
            raise ValueError("is_leaf must be a boolean")

        # Validate regex pattern and group count
        try:
            compiled = re.compile(self.pattern)
            group_count = compiled.groups
            if self.title_field and group_count < 1:
                raise ValueError(f"Pattern for level '{self.name}' must have at least one group for title.")
            # Note: We don't require two groups for description_field anymore
            # The first group will be used for title, and any remaining text will be used for description
        except re.error as e:
            raise ValueError(f"Invalid regular expression pattern for level '{self.name}': {e}")


@dataclass
class Config:
    """Configuration for parsing and structuring a document hierarchy.

    Attributes:
        root_name: Name of the root object.
        sections_field: Field name to store top-level sections.
        description_field: Field name for root description.
        levels: Dictionary of LevelConfig instances.
    """
    root_name: str
    sections_field: str
    description_field: str
    levels: Dict[str, LevelConfig] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.root_name, str):
            raise ValueError("root_name must be a string")
        if not isinstance(self.sections_field, str):
            raise ValueError("sections_field must be a string")
        if not isinstance(self.description_field, str):
            raise ValueError("description_field must be a string")
        if not isinstance(self.levels, dict):
            raise ValueError("levels must be a dictionary")

        for name, level in self.levels.items():
            if not isinstance(name, str):
                raise ValueError(f"Level name must be a string, got {type(name)}")
            if not isinstance(level, LevelConfig):
                raise ValueError(f"Level '{name}' must be an instance of LevelConfig")
            if level.name != name:
                raise ValueError(f"Level name mismatch: key is '{name}' but level.name is '{level.name}'")

        self.validate()

    def validate(self):
        """Validates internal consistency: parents, cycles, fields, regex."""
        # 1. Check that all parent levels exist
        for name, level in self.levels.items():
            if level.parent and level.parent not in self.levels:
                raise ValueError(f"Level '{name}' has undefined parent '{level.parent}'.")

        # 2. Detect cycles in parent relationships
        def detect_cycle(start, path):
            if start in path:
                raise ValueError(f"Cycle detected in hierarchy: {' -> '.join(path + [start])}")
            parent = self.levels[start].parent
            if parent:
                detect_cycle(parent, path + [start])

        for name in self.levels:
            detect_cycle(name, [])

        # 3. Ensure no conflicting field names
        for name, level in self.levels.items():
            fields = [level.title_field, level.description_field, level.sections_field, level.paragraph_field]
            non_null_fields = [f for f in fields if f]
            if len(set(non_null_fields)) < len(non_null_fields):
                raise ValueError(f"Level '{name}' has conflicting field names (e.g., same name used twice).")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self:
        """Creates a Config instance from a dictionary structure."""
        if not isinstance(data, dict):
            raise ValueError("Configuration data must be a dictionary")

        root_name = data.get("root_name")
        sections_field = data.get("sections_field")
        description_field = data.get("description_field")
        levels_data = data.get("levels", {})

        if not all([root_name, sections_field, description_field]):
            raise ValueError("Missing required fields: root_name, sections_field, description_field")

        levels = {}
        for name, level_data in levels_data.items():
            try:
                levels[name] = LevelConfig(**level_data)
            except TypeError as e:
                raise ValueError(f"Invalid level configuration for '{name}': {e}")

        return cls(
            root_name=root_name,
            sections_field=sections_field,
            description_field=description_field,
            levels=levels
        )
