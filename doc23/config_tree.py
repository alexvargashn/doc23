from dataclasses import dataclass, field
import re
from typing import Dict, Optional, Pattern, TypeVar, Generic, Any
from typing_extensions import Self


@dataclass
class LevelConfig:
    """Configuration for a document level in the hierarchy.
    
    This class defines how a particular level (e.g., book, chapter, article) should be
    identified and structured in the document.
    
    Attributes:
        pattern: Regular expression pattern to identify this level in the text
        name: Unique identifier for this level type
        title_field: Field name to store the title of this level
        description_field: Optional field name to store the description of this level
        sections_field: Optional field name to store child sections of this level
        paragraph_field: Optional field name to store paragraph content
        parent: Optional name of the parent level
    """
    pattern: str
    name: str
    title_field: str
    description_field: Optional[str] = None
    sections_field: Optional[str] = None
    paragraph_field: Optional[str] = None
    parent: Optional[str] = None
    
    def __post_init__(self):
        """Validate the configuration after initialization."""
        if not isinstance(self.pattern, str):
            raise ValueError("pattern must be a string")
        try:
            re.compile(self.pattern)
        except re.error as e:
            raise ValueError(f"Invalid regular expression pattern: {e}")
            
        if not isinstance(self.name, str):
            raise ValueError("name must be a string")
        if not isinstance(self.title_field, str):
            raise ValueError("title_field must be a string")
        if self.description_field is not None and not isinstance(self.description_field, str):
            raise ValueError("description_field must be a string or None")
        if self.sections_field is not None and not isinstance(self.sections_field, str):
            raise ValueError("sections_field must be a string or None")
        if self.paragraph_field is not None and not isinstance(self.paragraph_field, str):
            raise ValueError("paragraph_field must be a string or None")
        if self.parent is not None and not isinstance(self.parent, str):
            raise ValueError("parent must be a string or None")


@dataclass
class Config:
    """Configuration for document parsing and structure.
    
    This class defines the overall structure of how a document should be parsed
    and organized into a hierarchical tree.
    
    Attributes:
        root_name: Name of the root level in the document structure
        sections_field: Field name to store sections at each level
        description_field: Field name to store descriptions at each level
        levels: Dictionary mapping level names to their configurations
    """
    root_name: str
    sections_field: str
    description_field: str
    levels: Dict[str, LevelConfig] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate the configuration after initialization."""
        if not isinstance(self.root_name, str):
            raise ValueError("root_name must be a string")
        if not isinstance(self.sections_field, str):
            raise ValueError("sections_field must be a string")
        if not isinstance(self.description_field, str):
            raise ValueError("description_field must be a string")
        if not isinstance(self.levels, dict):
            raise ValueError("levels must be a dictionary")
            
        # Validate each level configuration
        for name, level in self.levels.items():
            if not isinstance(name, str):
                raise ValueError(f"Level name must be a string, got {type(name)}")
            if not isinstance(level, LevelConfig):
                raise ValueError(f"Level configuration must be a LevelConfig instance, got {type(level)}")
            if level.name != name:
                raise ValueError(f"Level name mismatch: config key is {name} but level.name is {level.name}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self:
        """Create a Config instance from a dictionary.
        
        Args:
            data: Dictionary containing configuration data
            
        Returns:
            Config instance
            
        Raises:
            ValueError: If the configuration data is invalid
        """
        if not isinstance(data, dict):
            raise ValueError("Configuration data must be a dictionary")
            
        # Extract and validate required fields
        root_name = data.get("root_name")
        sections_field = data.get("sections_field")
        description_field = data.get("description_field")
        levels_data = data.get("levels", {})
        
        if not all([root_name, sections_field, description_field]):
            raise ValueError("Missing required fields: root_name, sections_field, description_field")
            
        # Convert level configurations
        levels = {}
        for name, level_data in levels_data.items():
            try:
                levels[name] = LevelConfig(**level_data)
            except TypeError as e:
                raise ValueError(f"Invalid level configuration for {name}: {e}")
                
        return cls(
            root_name=root_name,
            sections_field=sections_field,
            description_field=description_field,
            levels=levels
        )