"""Synthetic (fictional) profile generator for the demo dashboard.

No real people or accounts are involved: each profile is a random set of
questionnaire answers drawn around a behaviour archetype.
"""
import csv
import math
import random

from .questions import CATEGORIES, QUESTIONS
from .scoring import score_assessment

# archetype -> typical answer risk (0-100) and share of the population
ARCHETYPES = {"cautious": (10, 0.30), "average": (45, 0.45), "oversharer": (80, 0.25)}


def _pick(options, center, rng):
    weights = [math.exp(-abs(risk - center) / 25) for _, risk in options]
    return rng.choices(range(len(options)), weights)[0]


def demo_answers(archetype=None, seed=None):
    """Random answers for one fictional persona: {question_id: option_index}."""
    rng = random.Random(seed)
    archetype = archetype or rng.choice(list(ARCHETYPES))
    center = ARCHETYPES[archetype][0] + rng.uniform(-10, 10)
    return {qid: _pick(q.options, center, rng) for qid, q in QUESTIONS.items()}


def generate_profiles(n=300, seed=42):
    rng = random.Random(seed)
    names = list(ARCHETYPES)
    shares = [ARCHETYPES[a][1] for a in names]
    rows = []
    for i in range(1, n + 1):
        arch = rng.choices(names, shares)[0]
        res = score_assessment(demo_answers(arch, seed=rng.random()))
        row = {"profile_id": f"SYN-{i:04d}", "archetype": arch,
               "overall": res.overall, "level": res.level}
        row.update({f"cat_{cid}": s for cid, s in res.category_scores.items()})
        row["weaknesses"] = "|".join(w["question_id"] for w in res.weaknesses)
        rows.append(row)
    return rows


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
