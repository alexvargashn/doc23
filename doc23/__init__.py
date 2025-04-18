"""
doc23 - A Python library for extracting text from documents and converting it into a structured JSON tree.
"""

from doc23.allowed_types import AllowedTypes
from doc23.config_tree import Config, LevelConfig
from doc23.gardener import Gardener
from doc23.main import Doc23

__all__ = ["Doc23", "LevelConfig", "Config", "AllowedTypes", "Gardener"]

__version__ = "0.1.0"
