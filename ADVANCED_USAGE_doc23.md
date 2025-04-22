
# ⚙️ Advanced Usage: doc23

This document complements the basic README with more advanced features and patterns
you can use when working with `doc23`.

---

## 📋 Custom Logging

You can enable logging for debugging or inspection:

```python
from doc23 import configure_logging
import logging

configure_logging(
    level=logging.DEBUG,
    log_file="doc23.log"
)
```

---

## 🧯 Error Handling

Wrap parsing with specific exception classes for clarity:

```python
from doc23 import Doc23, Config
from doc23.exceptions import Doc23Error, FileTypeError, ExtractionError

try:
    doc = Doc23("myfile.pdf", config)
    data = doc.prune()
except FileTypeError as e:
    print(f"Unsupported file: {e}")
except ExtractionError as e:
    print(f"Could not extract text: {e}")
except Doc23Error as e:
    print(f"General error: {e}")
```

---

## 🔁 Dynamically Selecting Configs

You may want to switch configs depending on the file name:

```python
if "civil_code" in filename:
    config = civil_config
elif "contracts" in filename:
    config = contract_config
else:
    config = default_config

doc = Doc23(filename, config)
structured = doc.prune()
```

---

## 🖼 OCR Auto-Detection for Images or Scanned PDFs

You can enable OCR in three ways:

```python
doc = Doc23("scanned.pdf", config)
text = doc.extract_text(scan_or_image=True)  # Force OCR

# OR let it auto-detect
text = doc.extract_text(scan_or_image="auto")

# Use text manually
data = doc.prune(text=text)
```

---

## 🛠 Custom `from_dict` Configuration

You can load a JSON or dict configuration dynamically:

```python
import json
from doc23 import Config

with open("config.json") as f:
    config_dict = json.load(f)

config = Config.from_dict(config_dict)
```

---

## 🧪 Writing Tests With Sample Texts

For your own documents, create representative examples and assert structure:

```python
from doc23 import Gardener

text = """
TITLE I
General Provisions

ARTICLE 1. This is the first article.
ARTICLE 2. This is the second.
"""

structure = Gardener(config).prune(text)

assert structure["sections"][0]["title"] == "I"
assert structure["sections"][0]["article"][1]["title"] == "2"
```

---

## 🧠 Tip: Multiple Leaf Types

If you have multiple leaves (e.g., articles and clauses), define both with `is_leaf=True`.

```python
"article": LevelConfig(..., is_leaf=True),
"clause": LevelConfig(..., is_leaf=True),
```

This lets both be routed into paragraph fields where applicable.

---

## 🧱 Advanced Integration

You can embed `doc23` into:

- CLI tools
- Flask/FastAPI APIs
- Django Admin Upload Process
- OCR pipelines using `watchdog` or scheduled jobs

---

## ✅ Ready for Production

- Validate configs up front
- Write small test samples
- Use logging while prototyping
- Catch and handle exceptions gracefully

---

For more info, visit the main README or contribute at:  
👉 [https://github.com/alexvargashn/doc23](https://github.com/alexvargashn/doc23)
