"""Scoring engine.

category score  = average risk (0-100) of the category's questions
base score      = weighted average of category scores
combination add = small bonus when two risky habits reinforce each other
overall score   = min(100, round(base + bonus))   (higher = MORE exposure)
"""
from dataclasses import dataclass, field

from .questions import CATEGORIES, QUESTIONS, CATEGORY_BY_ID

WEAKNESS_THRESHOLD = 50   # answer risk >= this is reported as a weakness
HIGH_SEVERITY = 75        # answer risk >= this is "High" severity
MAX_BONUS = 15

# (question A, min risk A, question B, min risk B, bonus, explanation)
COMPOUND_RULES = [
    ("mfa_1", 80, "password_reuse_1", 75, 8,
     "No (or unknown) MFA plus reused passwords: one breach elsewhere could unlock your account."),
    ("location_1", 80, "profile_visibility_1", 55, 5,
     "Frequent real-time location posts on a widely visible profile reveal your routine."),
    ("unknown_requests_1", 80, "suspicious_links_1", 60, 4,
     "Accepting strangers and clicking unverified links is a classic phishing path."),
    ("birthday_2", 60, "personal_info_1", 45, 4,
     "Quiz-style answers plus detailed bio info can help someone guess security questions."),
    ("social_engineering_2", 60, "login_alerts_1", 80, 3,
     "Acting on urgent messages with no login alerts makes takeover harder to notice."),
]


def risk_level(score: int) -> str:
    if score <= 20:
        return "LOW"
    if score <= 40:
        return "MODERATE"
    if score <= 70:
        return "HIGH"
    return "CRITICAL"


@dataclass
class Result:
    overall: int
    base: float
    bonus: int
    level: str
    category_scores: dict
    question_risks: dict
    weaknesses: list = field(default_factory=list)
    compound: list = field(default_factory=list)


def score_assessment(answers: dict) -> Result:
    """answers: {question_id: option_index}. Raises ValueError on bad input."""
    missing = [qid for qid in QUESTIONS if qid not in answers]
    if missing:
        raise ValueError(f"Missing answers for: {', '.join(missing)}")

    risks, weaknesses = {}, []
    for qid, q in QUESTIONS.items():
        idx = answers[qid]
        if not isinstance(idx, int) or not 0 <= idx < len(q.options):
            raise ValueError(f"Invalid option index for {qid}: {idx!r}")
        label, risk = q.options[idx]
        risks[qid] = risk
        if risk >= WEAKNESS_THRESHOLD:
            weaknesses.append({
                "question_id": qid, "category": q.category,
                "category_name": CATEGORY_BY_ID[q.category].name,
                "question": q.text, "answer": label, "risk": risk,
                "severity": "High" if risk >= HIGH_SEVERITY else "Medium",
                "weakness": q.weakness,
            })

    cat_scores = {
        c.id: round(sum(risks[q.id] for q in c.questions) / len(c.questions), 1)
        for c in CATEGORIES
    }
    total_w = sum(c.weight for c in CATEGORIES)
    base = sum(cat_scores[c.id] * c.weight for c in CATEGORIES) / total_w

    compound, bonus = [], 0
    for a, ta, b, tb, pts, msg in COMPOUND_RULES:
        if risks[a] >= ta and risks[b] >= tb:
            compound.append({"message": msg, "bonus": pts})
            bonus += pts
    bonus = min(bonus, MAX_BONUS)

    overall = min(100, round(base + bonus))
    weaknesses.sort(
        key=lambda w: w["risk"] * CATEGORY_BY_ID[w["category"]].weight, reverse=True)
    return Result(overall, round(base, 1), bonus, risk_level(overall),
                  cat_scores, risks, weaknesses, compound)
