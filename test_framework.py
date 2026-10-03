import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from privacy_framework.questions import CATEGORIES, QUESTIONS
from privacy_framework.recommendations import build_checklist, build_recommendations
from privacy_framework.report import build_html, build_markdown
from privacy_framework.scoring import risk_level, score_assessment
from privacy_framework.synthetic import generate_profiles


def uniform(pick):
    """Answers using the safest (min) or riskiest (max) option for every question."""
    out = {}
    for qid, q in QUESTIONS.items():
        risks = [r for _, r in q.options]
        out[qid] = risks.index(pick(risks))
    return out


class TestFramework(unittest.TestCase):
    def test_question_bank_shape(self):
        self.assertEqual(len(CATEGORIES), 20)
        self.assertEqual(len(QUESTIONS), 40)
        for q in QUESTIONS.values():
            labels = [o[0] for o in q.options]
            self.assertEqual(len(labels), len(set(labels)), q.id)
            self.assertTrue(all(0 <= r <= 100 for _, r in q.options))

    def test_level_boundaries(self):
        cases = {0: "LOW", 20: "LOW", 21: "MODERATE", 40: "MODERATE",
                 41: "HIGH", 70: "HIGH", 71: "CRITICAL", 100: "CRITICAL"}
        for score, level in cases.items():
            self.assertEqual(risk_level(score), level, score)

    def test_safest_answers_are_low(self):
        res = score_assessment(uniform(min))
        self.assertEqual(res.overall, 0)
        self.assertEqual(res.level, "LOW")
        self.assertEqual(res.weaknesses, [])

    def test_riskiest_answers_are_critical_and_capped(self):
        res = score_assessment(uniform(max))
        self.assertEqual(res.overall, 100)
        self.assertEqual(res.level, "CRITICAL")
        self.assertLessEqual(res.bonus, 15)

    def test_missing_and_invalid_answers(self):
        with self.assertRaises(ValueError):
            score_assessment({})
        bad = uniform(min)
        bad["mfa_1"] = 99
        with self.assertRaises(ValueError):
            score_assessment(bad)

    def test_compound_bonus(self):
        answers = uniform(min)
        no_mfa = [r for _, r in QUESTIONS["mfa_1"].options]
        answers["mfa_1"] = no_mfa.index(100)
        reuse = [r for _, r in QUESTIONS["password_reuse_1"].options]
        answers["password_reuse_1"] = reuse.index(100)
        res = score_assessment(answers)
        self.assertEqual(res.bonus, 8)
        self.assertEqual(len(res.compound), 1)

    def test_recommendations_report_and_checklist(self):
        res = score_assessment(uniform(max))
        self.assertGreater(len(build_recommendations(res)), 0)
        self.assertEqual(len(build_checklist(res)), 40)
        md = build_markdown(res)
        self.assertIn("Privacy Risk Score", md)
        self.assertIn("not a guarantee", md.lower())
        self.assertIn("<html", build_html(res))

    def test_synthetic_profiles_are_deterministic(self):
        a = generate_profiles(20, seed=1)
        b = generate_profiles(20, seed=1)
        self.assertEqual(a, b)
        self.assertTrue(all(0 <= r["overall"] <= 100 for r in a))
        self.assertTrue(all(r["profile_id"].startswith("SYN-") for r in a))


if __name__ == "__main__":
    unittest.main()
