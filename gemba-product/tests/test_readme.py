import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
SKILLS = os.path.join(ROOT, "skills")

METHODS = {
    "pitch": ["Jobs to be Done"],
    "interview-kit": ["past facts"],
    "story-map": ["User Story Mapping", "Patton"],
    "architecture": ["ADR", "C4"],
}


def skills_section():
    """The bullets of the README's Skills section, by skill name."""
    with open(README, encoding="utf-8") as readme:
        body = readme.read()
    section = re.search(r"^## Skills\n(.*?)(?=^## |\Z)", body, re.M | re.S)
    if not section:
        return {}
    bullets = re.findall(r"^- `([a-z-]+)`(.*(?:\n(?!- |#).*)*)", section.group(1), re.M)
    return {name: text for name, text in bullets}


class Skills(unittest.TestCase):
    def test_names_the_method_of_each_skill(self):
        bullets = skills_section()
        for skill, methods in METHODS.items():
            with self.subTest(skill=skill):
                self.assertIn(skill, bullets, f"the README does not name {skill}")
                for method in methods:
                    self.assertIn(method, bullets[skill],
                                  f"{skill} does not name its method: {method}")

    def test_covers_every_skill_in_the_plugin(self):
        installed = {name for name in os.listdir(SKILLS)
                     if os.path.isfile(os.path.join(SKILLS, name, "SKILL.md"))}
        self.assertEqual(set(skills_section()), installed)


if __name__ == "__main__":
    unittest.main()
