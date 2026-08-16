import json
import unittest
from pathlib import Path

from ai_service import demo_plan


class ProfileTest(unittest.TestCase):
    def test_nyra_profile_and_routine_are_loaded(self):
        data = json.loads(Path("data/littlebloom.json").read_text(encoding="utf-8"))
        profile = data["profile"]

        self.assertEqual(profile["name"], "Nyra")
        self.assertEqual(len(profile["routine"]), 15)
        self.assertIn("never to eat", profile["likes"])
        self.assertEqual(len(demo_plan(profile)), 5)

    def test_second_language_adds_language_learning_activity(self):
        data = json.loads(Path("data/littlebloom.json").read_text(encoding="utf-8"))
        profile = {**data["profile"], "second_language": "Spanish"}

        plan = demo_plan(profile)

        self.assertTrue(any("Spanish" in item["title"] for item in plan))


if __name__ == "__main__":
    unittest.main()
