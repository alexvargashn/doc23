# doc23

A Python library for extracting text from documents and converting it into a structured JSON tree.

## Features

- Extract text from various document formats (PDF, DOCX, TXT, RTF, ODT, MD, etc.)
- OCR support for scanned documents and images
- Flexible configuration for defining document structure
- Hierarchical parsing of document content

## Installation

```bash
pip install doc23
```

### Dependencies

- Python 3.10+
- For OCR functionality:
  - Tesseract OCR (system installation required)
  - pytesseract package

## Basic Usage

```python
from doc23 import Doc23, Config, LevelConfig

# Define your document structure
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
        "chapter": LevelConfig(
            pattern=r"^CHAPTER\s+(.+)$",
            name="chapter",
            title_field="title",
            description_field="description",
            sections_field="sections",
            parent="book"
        ),
        "article": LevelConfig(
            pattern=r"^ARTICLE\s+(\d+)\.\s*(.*)$",
            name="article",
            title_field="title",
            description_field="content",
            paragraph_field="paragraphs",
            parent="chapter"
        )
    }
)

# Process a document
doc = Doc23("my_document.pdf", config)
structure = doc.prune()

# Use the structured content
print(structure["sections"][0]["title"])  # First book title
```

## Advanced Usage

### OCR for Scanned Documents

```python
# Enable OCR for scanned documents
doc = Doc23("scanned_document.pdf", config)
structure = doc.prune(text=doc.extract_text(scan_or_image=True))

# Or let the library detect if OCR is needed
structure = doc.prune(text=doc.extract_text(scan_or_image="auto"))
```

### Custom Logging

```python
from doc23 import configure_logging
import logging

# Configure logging to file with debug level
configure_logging(
    level=logging.DEBUG,
    log_file="doc23.log"
)

# Continue with normal usage
doc = Doc23("my_document.pdf", config)
```

## Document Structure Definition

The document structure is defined using `Config` and `LevelConfig` objects:

- `Config`: Defines the overall structure and contains multiple level configurations
- `LevelConfig`: Defines how to recognize and structure a specific level in the document

Example configuration for a legal document:

```python
config = Config(
    root_name="legal_document",
    sections_field="sections",
    description_field="description",
    levels={
        "title": LevelConfig(
            pattern=r"^TITLE\s+([^\n]+)$",
            name="title",
            title_field="title",
            description_field="description",
            sections_field="chapters"
        ),
        "chapter": LevelConfig(
            pattern=r"^CHAPTER\s+([^\n]+)$",
            name="chapter",
            title_field="title",
            description_field="description",
            sections_field="articles",
            parent="title"
        ),
        "article": LevelConfig(
            pattern=r"^ARTICLE\s+(\d+(?:-\w)?)\.\s*(.+)?$",
            name="article",
            title_field="number",
            description_field="content",
            paragraph_field="paragraphs",
            parent="chapter"
        )
    }
)
```

## Error Handling

The library provides specific exception classes for better error handling:

```python
from doc23 import Doc23, Config, Doc23Error, FileTypeError, ExtractionError

try:
    doc = Doc23("document.pdf", config)
    structure = doc.prune()
except FileTypeError as e:
    print(f"Unsupported file type: {e}")
except ExtractionError as e:
    print(f"Text extraction failed: {e}")
except Doc23Error as e:
    print(f"General error: {e}")
```

## License

MIT

