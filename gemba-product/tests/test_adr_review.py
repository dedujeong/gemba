import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHITECTURE = os.path.join(ROOT, "skills", "architecture")
SKILL = os.path.join(ARCHITECTURE, "SKILL.md")
HEURISTICS = os.path.join(ARCHITECTURE, "references", "adr-heuristics.md")


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def section(text, heading):
    """The body of a `## <heading>` section, up to the next `## ` heading."""
    parts = text.split("## " + heading)
    return parts[1].split("\n## ")[0] if len(parts) > 1 else ""


class AdrHeuristics(unittest.TestCase):
    def test_the_reference_has_the_four_heuristics_each_with_its_question_and_when_to_skip(self):
        body = read(HEURISTICS)
        for heuristic in ("Browser and server boundary", "Gaps between ADRs", "Limited resource", "Contradictions"):
            self.assertIn(heuristic, body)
        self.assertEqual(body.count("| Heuristic | Question | Skip when |"), 1)


class ReviewBeforeAccepting(unittest.TestCase):
    def review(self):
        return section(read(SKILL), "6. Review the ADRs before accepting them")

    def test_the_skill_reviews_each_adr_and_the_whole_set_with_the_reference(self):
        text = self.review()
        self.assertIn("references/adr-heuristics.md", text)
        self.assertIn("each ADR and the whole set", text)
        self.assertIn("Before any ADR of a set is marked as accepted", text)
        self.assertIn("When the review finds nothing, say so in one line and go on with the acceptance the person asked for", text)
        self.assertIn("A finding rests on what the brief, the Story Map or the ADRs say, never on what a product like this usually needs", text)
        self.assertIn("If this conversation already holds the review of the set with no open question, do not run it again", text)

    def test_the_contradictions_are_also_looked_for_among_the_accepted_adrs_of_the_space(self):
        text = self.review()
        self.assertIn("ADRs already accepted in the `Decisions` folder", text)
        self.assertIn("never edits the accepted one", text)
        self.assertIn("a new ADR that replaces it", text)

    def test_the_questions_of_the_review_are_asked_in_one_single_round_naming_adr_and_heuristic(self):
        text = self.review()
        self.assertIn("one single round", text)
        self.assertIn("all the questions", text)
        self.assertIn("«ADR: <the ADR or the set>. Heurística: <the heuristic that found it>. ¿...?»", text)

    def test_the_review_comes_before_the_work_for_the_version(self):
        body = read(SKILL)
        self.assertLess(body.index("## 6. Review the ADRs before accepting them"), body.index("## 7. Propose the work for the version"))


if __name__ == "__main__":
    unittest.main()
