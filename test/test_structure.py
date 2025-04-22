import unittest
from doc23.config_tree import Config, LevelConfig
from doc23.gardener import Gardener

sample_text = """
CHAPTER I
Laying Plans

1. Sun Tzu said: The art of war is of vital importance to the State.
2. It is a matter of life and death, a road either to safety or to ruin.

CHAPTER II
Waging War

1. In the operations of war, where there are in the field a thousand swift chariots...
"""

class TestDoc23Structure(unittest.TestCase):

    def setUp(self):
        self.config = Config(
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

    def test_structure_parsing(self):
        gardener = Gardener(self.config)
        result = gardener.prune(sample_text)
        self.assertIn("chapters", result)
        self.assertGreater(len(result["chapters"]), 0)
        first_chapter = result["chapters"][0]
        self.assertEqual(first_chapter["title"], "I")
        self.assertIn("paragraphs", first_chapter)
        self.assertGreater(len(first_chapter["paragraphs"]), 1)
        self.assertEqual(first_chapter["paragraphs"][0]["number"], "1")
        self.assertTrue(first_chapter["paragraphs"][0]["text"].startswith("Sun Tzu said"))

    def test_empty_input(self):
        gardener = Gardener(self.config)
        with self.assertRaises(ValueError):
            gardener.prune("   ")


if __name__ == '__main__':
    unittest.main()
