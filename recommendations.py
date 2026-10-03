"""Turn a scoring Result into prioritised recommendations and a checklist."""
from .questions import CATEGORIES, QUESTIONS, CATEGORY_BY_ID

CHECKLIST_DONE_BELOW = 40  # answer risk below this counts as "done"


def build_recommendations(result):
    recs = []
    for c in result.compound:
        recs.append({
            "priority": "Critical combination",
            "category": "Combined risk",
            "issue": c["message"],
            "action": "Fix at least one side of this combination today "
                      "(e.g. enable MFA, tighten the audience, stop the risky habit).",
        })
    for w in result.weaknesses:
        q = QUESTIONS[w["question_id"]]
        recs.append({
            "priority": "High" if w["severity"] == "High" else "Medium",
            "category": w["category_name"],
            "issue": w["weakness"],
            "action": q.fix,
        })
    return recs


def build_checklist(result):
    items = []
    for c in CATEGORIES:
        for q in c.questions:
            items.append({
                "category": c.name,
                "item": q.fix,
                "done": result.question_risks[q.id] < CHECKLIST_DONE_BELOW,
            })
    return items
