from dataclasses import dataclass, field
import re
from typing import Dict, Optional, TypedDict


# Setup for each level of the document
@dataclass
class LevelConfig(TypedDict, total=False):
    """_summary_

    Args:
        TypedDict (_type_): _description_
        total (bool, optional): _description_. Defaults to False.

    Raises:
        ValueError: _description_
    """

    pattern: str  # Patter to be found for the title
    title_field: str  # Field to be used as title tag
    description_field: str  # Field to be used as description tag
    sections_field: str  # Field to be used as sections tag
    paragraph_field: Optional[str]  # Field to be used as paragraph tag
    parent: Optional[str]  # Parent level

    def __post_init__(self):
        if not isinstance(self.pattern, str) or not re.compile(self.pattern):
            raise ValueError(f"The pattern'{self.pattern}' is not valid.")


# Setup for the document
@dataclass
class Config(TypedDict):
    sections_field: str  # Field to be used as sections tag
    description_field: str  # Field to be used as description tag
    levels: Dict[str, LevelConfig] = field(
        default_factory=dict
    )  # Levels of the document
