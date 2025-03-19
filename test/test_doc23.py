import unittest
from pathlib import Path
import json
from doc23 import Doc23, Config


class TestDoc23(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup test files and configuration before running tests."""
        cls.config_path = "test/config.json"
        cls.files = {
            "docx": "test/test_document.docx",
            "pdf": "test/test_document.pdf",
            "txt": "test/test_document.txt",
            "odt": "test/test_document.odt",
        }

        with open(cls.config_path, "r", encoding="utf-8") as f:
            cls.config = Config(json.load(f))

    def test_extract_text_docx(self):
        """Test text extraction from a DOCX file."""
        doc = Doc23(self.files["docx"], self.config)
        text = doc.extract_text()
        self.assertIn("The Evolution of Technology", text)
        self.assertIn(
            "Technology has been an integral part of human civilization since the dawn of time",
            text,
        )

    def test_extract_text_pdf(self):
        """Test text extraction from a PDF file."""
        doc = Doc23(self.files["pdf"], self.config)
        text = doc.extract_text()
        self.assertIn("The Evolution of Technology", text)
        self.assertIn(
            "Technology has been an integral part of human civilization since the dawn of time",
            text,
        )

    def test_extract_text_txt(self):
        """Test text extraction from a TXT file."""
        doc = Doc23(self.files["txt"], self.config)
        text = doc.extract_text()
        self.assertIn("The Evolution of Technology", text)
        self.assertIn(
            "Technology has been an integral part of human civilization since the dawn of time",
            text,
        )

    def test_extract_text_odt(self):
        """Test text extraction from an ODT file."""
        doc = Doc23(self.files["odt"], self.config)
        text = doc.extract_text()
        self.assertIn("The Evolution of Technology", text)
        # self.assertIn(
        #     "Technology has been an integral part of human civilization since the dawn of time",
        #     text,
        # )

    def test_prune(self):
        """Test the prune function to generate the expected JSON structure."""
        doc = Doc23(self.files["txt"], self.config)
        json_output = doc.prune()
        # Pretty-print the JSON output
        print(json.dumps(json_output, indent=4, ensure_ascii=False))
        self.assertIn("document_structure", json_output)
        self.assertIn("sections", json_output["document_structure"])

    def test_invalid_file(self):
        """Test error handling when an invalid file is provided."""
        with self.assertRaises(ValueError):
            Doc23("invalid_file.xyz", self.config).extract_text()


if __name__ == "__main__":
    unittest.main()
