<p align="center">
  <img src="./assets/doc23-banner-tree.png" alt="doc23 banner" width="400" height="300" style="border-radius: 20px;" />
</p>

# 📚 doc23

**Convert documents into structured JSON effortlessly.**  
A Python library for extracting text from various document formats and structuring it hierarchically into JSON.

---

## 📌 Features

- ✅ Extract text from PDFs, DOCX, TXT, RTF, ODT, MD, and images.
- 🖼️ OCR support for scanned documents and images.
- ⚙️ Flexible configuration using regex patterns and field mapping.
- 🌳 Nested hierarchical structure output in JSON.
- ✨ Explicit leaf-level control using `is_leaf=True`.
- 🔍 Built-in validations to catch config mistakes (regex, hierarchy, field conflicts).
- 🧪 Comprehensive pytest suite with coverage reporting.

---

## 📦 Installation

```bash
pip install doc23
```

To enable OCR:
```bash
sudo apt install tesseract-ocr
pip install pytesseract
```

---

## 🚀 Quickstart Example

### Basic Text Extraction
```python
from doc23 import extract_text

# Extract text from any supported document
text = extract_text("document.pdf", scan_or_image="auto")
print(text)
```

### Structured Document Parsing
```python
from doc23 import Doc23, Config, LevelConfig

config = Config(
    root_name="art_of_war",
    sections_field="chapters",
    description_field="description",
    levels={
        "chapter": LevelConfig(
            pattern=r"^CHAPTER\s+([IVXLCDM]+)\n(.+)$",
            name="chapter",
            title_field="title",
            description_field="description",
            sections_field="paragraphs"
        ),
        "paragraph": LevelConfig(
            pattern=r"^(\d+)\.\s+(.+)$",
            name="paragraph",
            title_field="number",
            description_field="text",
            is_leaf=True
        )
    }
)

with open("art_of_war.txt") as f:
    text = f.read()

doc = Doc23(text, config)
structure = doc.prune()

print(structure["chapters"][0]["title"])  # → I
```

---

## 🧾 Output Example

```json
{
  "description": "",
  "chapters": [
    {
      "type": "chapter",
      "title": "I",
      "description": "Laying Plans",
      "paragraphs": [
        {
          "type": "paragraph",
          "number": "1",
          "text": "Sun Tzu said: The art of war is of vital importance to the State."
        }
      ]
    }
  ]
}
```

---

## 🛠️ Document Configuration

Use `Config` and `LevelConfig` to define how your document is parsed:

| Field | Purpose |
|-------|---------|
| `pattern` | Regex to match each level |
| `title_field` | Field to assign the first regex group |
| `description_field` | (Optional) Field for second group |
| `sections_field` | (Optional) Where sublevels go |
| `paragraph_field` | (Optional) Where text/nodes go if leaf |
| `is_leaf` | (Optional) Forces this level to be terminal |

### Capture Group Rules

| Fields Defined | Required Groups in Regex |
|----------------|--------------------------|
| `title_field` only | ≥1 |
| `title_field` + `description_field` | ≥2 |
| `title_field` + `paragraph_field` | ≥1 (second group optional) |

---

## 🏗️ Architecture Overview

doc23 consists of several key components:

```
Doc23 (core.py)
├── Extractors (extractors/)
│   ├── PDFExtractor
│   ├── DocxExtractor
│   ├── TextExtractor
│   └── ...
├── Config (config_tree.py)
│   └── LevelConfig
└── Gardener (gardener.py)
```

1. **Doc23**: Main entry point, handles file detection and orchestration
2. **Extractors**: Convert various document types to plain text
3. **Config**: Defines how to structure the document hierarchy
4. **Gardener**: Parses text and builds the JSON structure

---

## ✅ Built-in Validation

The library validates your config when creating `Doc23`:

- ✋ Ensures all parents exist.
- 🔁 Detects circular relationships.
- ⚠️ Checks field name reuse.
- 🧪 Verifies group counts match pattern.

If any issue is found, a `ValueError` will be raised immediately.

---

## 🧪 Testing

The library includes a comprehensive test suite covering various scenarios:

### Basic Initialization
```python
def test_gardener_initialization():
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
    assert gardener.leaf == "article"
```

### Document Structure
```python
def test_prune_basic_structure():
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
More content"""
    result = gardener.prune(text)
    assert result["sections"][0]["title"] == "First Book"
    assert result["sections"][0]["sections"][0]["paragraphs"] == ["This is article content", "More content"]
```

### Edge Cases
```python
def test_prune_empty_document():
    config = Config(
        root_name="document",
        sections_field="sections",
        description_field="description",
        levels={}
    )
    gardener = Gardener(config)
    result = gardener.prune("")
    assert result["sections"] == []
```

### Free Text Handling
```python
def test_prune_with_free_text():
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
            )
        }
    )
    gardener = Gardener(config)
    text = """This is free text at the top level
TITLE First Title
Title description"""
    result = gardener.prune(text)
    assert result["description"] == "This is free text at the top level"
```

Run tests with:
```bash
python -m pytest tests/
```

---

## ❓ Troubleshooting FAQ

### OCR not working
Make sure Tesseract is installed and accessible in your PATH.

### Text extraction issues
Different document formats may require specific libraries. Check your dependencies:
- PDF: pdfplumber, pdf2image
- DOCX: docx2txt
- ODT: odf

### Regex pattern not matching
Test your patterns with tools like [regex101.com](https://regex101.com) and ensure you have the correct number of capture groups.

---

## 🔄 Compatibility

- Python 3.8+
- Tested on Linux, macOS, and Windows

---

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT

---

## 🔗 Resources

- [Project Gutenberg – Public Domain Texts](https://www.gutenberg.org)
- [Tesseract OCR Wiki](https://github.com/tesseract-ocr/tesseract/wiki)
- [GitHub Repository](https://github.com/alexvargashn/doc23)


---

## 🧠 Advanced Usage

For advanced patterns, dynamic configs, exception handling and OCR examples, see:

📄 [ADVANCED_USAGE_doc23.md](ADVANCED_USAGE_doc23.md)
