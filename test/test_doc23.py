import unittest
from pathlib import Path
import json
from doc23 import Doc23, Config
from doc23.config_tree import LevelConfig


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
            cls.config = Config.from_dict(json.load(f))

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

    def test_prune_with_legal_document(self):
        """Test the prune method with a legal document structure."""
        # Create test configuration
        book_level = LevelConfig(
            pattern="^(LIBRO|LBRO)\\s+[^\\n]+",
            name="book",
            title_field="title",
            description_field="description",
            sections_field="sections",
            paragraph_field=None,
            parent=None
        )

        title_level = LevelConfig(
            pattern="^TITULO\\s+[^\\n]+",
            name="title",
            title_field="title",
            description_field="description",
            sections_field="sections",
            paragraph_field="article",
            parent="book"
        )

        chapter_level = LevelConfig(
            pattern="^CAPITULO\\s+[^\\n]+",
            name="chapter",
            title_field="title",
            description_field="description",
            sections_field="sections",
            paragraph_field="article",
            parent="title"
        )

        article_level = LevelConfig(
            pattern="^(ARTICULO\\s+\\d+(?:-?[A-Za-z])?)\\.\\s*(.+)",
            name="article",
            title_field="title",
            description_field=None,
            sections_field=None,
            paragraph_field="content",
            parent=None
        )

        config = Config(
            root_name="MyDocument",
            sections_field="sections",
            description_field="description",
            levels={
                "book": book_level,
                "title": title_level,
                "chapter": chapter_level,
                "article": article_level
            }
        )

        # Create test document content
        test_content = """
        LIBRO PRIMERO
        TITULO PRIMERO
        CAPITULO PRIMERO
        ARTICULO 1. Este es el primer artículo.
        ARTICULO 2. Este es el segundo artículo.
        CAPITULO SEGUNDO
        ARTICULO 3. Este es el tercer artículo.
        TITULO SEGUNDO
        ARTICULO 4. Este es el cuarto artículo.
        """

        # Create a temporary file with the test content
        test_file = Path("test/test_legal_document.txt")
        test_file.write_text(test_content, encoding="utf-8")

        try:
            # Test the prune method
            doc = Doc23(test_file, config)
            result = doc.prune()

            # Verify the structure
            self.assertIn("sections", result)
            self.assertIsInstance(result["sections"], list)
            
            # Verify book level
            self.assertEqual(len(result["sections"]), 1)
            book = result["sections"][0]
            self.assertEqual(book["title"], "LIBRO PRIMERO")
            
            # Verify titles
            self.assertIn("sections", book)
            self.assertEqual(len(book["sections"]), 2)
            
            # Verify first title
            title1 = book["sections"][0]
            self.assertEqual(title1["title"], "TITULO PRIMERO")
            
            # Verify chapters in first title
            self.assertIn("sections", title1)
            self.assertEqual(len(title1["sections"]), 2)
            
            # Verify articles in first chapter
            chapter1 = title1["sections"][0]
            self.assertEqual(chapter1["title"], "CAPITULO PRIMERO")
            self.assertIn("article", chapter1)
            self.assertEqual(len(chapter1["article"]), 2)
            
            # Verify article content
            article1 = chapter1["article"][0]
            self.assertEqual(article1["title"], "ARTICULO 1")
            self.assertEqual(article1["content"], "Este es el primer artículo.")

        finally:
            # Clean up the temporary file
            test_file.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
