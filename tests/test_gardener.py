"""
Tests for the Gardener class.
"""

import pytest

from doc23.config_tree import Config, LevelConfig
from doc23.gardener import Gardener


def test_gardener_initialization():
    """Test Gardener initialization."""
    config = Config(
        root_name="document",
        sections_field="sections",
        description_field="description",
        levels={
            "book": LevelConfig(
                pattern=r"^BOOK\s+(.+)$",
                name="book",
                title_field="title",
                description_field="description",
                sections_field="sections"
            ),
            "article": LevelConfig(
                pattern=r"^ARTICLE\s+(\d+)\.\s*(.*)$",
                name="article",
                title_field="title",
                description_field="content",
                paragraph_field="paragraphs",
                parent="book"
            )
        }
    )
    gardener = Gardener(config)
    
    # Check that patterns were compiled
    assert len(gardener.patterns) == 2
    assert "book" in gardener.patterns
    assert "article" in gardener.patterns
    
    # Check leaf detection
    assert gardener.leaf == "article"
    
    # Check ranking
    assert gardener.rank["book"] < gardener.rank["article"]


def test_prune_basic_structure():
    """Test basic document pruning."""
    config = Config(
        root_name="document",
        sections_field="sections",
        description_field="description",
        levels={
            "book": LevelConfig(
                pattern=r"^BOOK\s+(.+)$",
                name="book",
                title_field="title",
                description_field="description",
                sections_field="sections"
            ),
            "article": LevelConfig(
                pattern=r"^ARTICLE\s+(\d+)\.\s*(.*)$",
                name="article",
                title_field="title",
                description_field="content",
                paragraph_field="paragraphs",
                parent="book"
            )
        }
    )
    gardener = Gardener(config)
    
    text = """BOOK First Book
This is a description
ARTICLE 1. First article
This is article content
More content
ARTICLE 2. Second article
Another article"""
    
    result = gardener.prune(text)
    
    # Check top level structure
    assert "title" in result
    assert "description" in result
    assert "sections" in result
    
    # Check book level
    assert len(result["sections"]) == 1
    book = result["sections"][0]
    assert book["title"] == "First Book"
    assert book["description"] == "This is a description"
    
    # Check articles
    assert "sections" in book
    assert len(book["sections"]) == 2
    
    article1 = book["sections"][0]
    assert article1["title"] == "1"
    assert article1["content"] == "First article"
    assert article1["paragraphs"] == ["This is article content", "More content"]
    
    article2 = book["sections"][1]
    assert article2["title"] == "2"
    assert article2["content"] == "Second article"
    assert article2["paragraphs"] == ["Another article"]


def test_prune_empty_document():
    """Test pruning an empty document."""
    config = Config(
        root_name="document",
        sections_field="sections",
        description_field="description",
        levels={}
    )
    gardener = Gardener(config)
    
    result = gardener.prune("")
    
    assert result["title"] == ""
    assert result["description"] == ""
    assert result["sections"] == []


def test_prune_with_free_text():
    """Test pruning with free text at various levels."""
    config = Config(
        root_name="document",
        sections_field="sections",
        description_field="description",
        levels={
            "title": LevelConfig(
                pattern=r"^TITLE\s+(.+)$",
                name="title",
                title_field="title",
                description_field="description",
                sections_field="sections"
            ),
            "chapter": LevelConfig(
                pattern=r"^CHAPTER\s+(.+)$",
                name="chapter",
                title_field="title",
                description_field="description",
                sections_field="sections",
                parent="title"
            )
        }
    )
    gardener = Gardener(config)
    
    text = """This is free text at the top level
TITLE First Title
Title description
More title info
CHAPTER First Chapter
Chapter description
TITLE Second Title
Free text after title"""
    
    result = gardener.prune(text)
    
    # Check top level structure and free text
    assert result["description"] == "This is free text at the top level"
    assert len(result["sections"]) == 2
    
    # Check first title
    title1 = result["sections"][0]
    assert title1["title"] == "First Title"
    assert title1["description"] == "Title description More title info"
    
    # Check chapter under first title
    chapter = title1["sections"][0]
    assert chapter["title"] == "First Chapter"
    assert chapter["description"] == "Chapter description"
    
    # Check second title
    title2 = result["sections"][1]
    assert title2["title"] == "Second Title"
    assert title2["description"] == "Free text after title" 