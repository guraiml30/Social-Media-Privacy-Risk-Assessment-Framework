"""Command-line version of the assessment.

  python cli.py --demo                 score a random fictional persona
  python cli.py --demo --archetype oversharer
  python cli.py --interactive          answer the questions yourself (demo data only!)
"""
import argparse
from pathlib import Path

from privacy_framework import DISCLAIMER
from privacy_framework.questions import CATEGORIES, QUESTIONS
from privacy_framework.scoring import score_assessment
from privacy_framework.synthetic import demo_answers, ARCHETYPES
from privacy_framework.report import build_markdown, build_html


def ask_all():
    answers = {}
    for c in CATEGORIES:
        print(f"\n=== {c.name} ===")
        for q in c.questions:
            print(f"\n{q.text}")
            for i, (label, _) in enumerate(q.options, 1):
                print(f"  {i}. {label}")
            while True:
                raw = input("Your choice: ").strip()
                if raw.isdigit() and 1 <= int(raw) <= len(q.options):
                    answers[q.id] = int(raw) - 1
                    break
                print("Please enter a valid number.")
    return answers


def main():
    p = argparse.ArgumentParser(description="Social Media Privacy Risk Assessment")
    p.add_argument("--demo", action="store_true", help="use a random fictional persona")
    p.add_argument("--archetype", choices=list(ARCHETYPES), help="persona type for --demo")
    p.add_argument("--interactive", action="store_true", help="answer the questions")
    p.add_argument("--out", default="reports", help="folder for the report files")
    args = p.parse_args()
    if not (args.demo or args.interactive):
        p.error("choose --demo or --interactive")

    print(DISCLAIMER)
    answers = demo_answers(args.archetype) if args.demo else ask_all()
    label = "Fictional demo persona" if args.demo else "Interactive demo user"
    res = score_assessment(answers)

    print(f"\nPrivacy Risk Score: {res.overall}/100  ->  {res.level}")
    print("\nCategory scores:")
    for c in CATEGORIES:
        print(f"  {c.name:<36}{res.category_scores[c.id]:>6}")
    print(f"\nWeaknesses detected: {len(res.weaknesses)}")
    for w in res.weaknesses[:5]:
        print(f"  [{w['severity']}] {w['category_name']}: {w['weakness']}")

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    (out / "report.md").write_text(build_markdown(res, label), encoding="utf-8")
    (out / "report.html").write_text(build_html(res, label), encoding="utf-8")
    print(f"\nFull report saved to {out}/report.md and {out}/report.html")


if __name__ == "__main__":
    main()
