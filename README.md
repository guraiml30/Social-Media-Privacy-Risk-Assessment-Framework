# 🛡️ Social Media Privacy Risk Assessment Framework

A **defensive**, educational tool where a user answers 40 questions about their social-media privacy settings and habits. It returns a **Privacy Risk Score (0-100)**, a risk level, category scores, detected weaknesses, prioritised recommendations, a privacy checklist and an optional report.

> **Higher score = higher exposure/risk.**
> This is an educational framework, **not** a guarantee that an account will or will not be compromised.

## Ethics and scope

- Uses **synthetic fictional profiles** and voluntarily entered demo answers only.
- **No** scraping, **no** account enumeration, **no** bypassing privacy settings, **no** tracking or profiling of real people.
- Evaluates *configuration and exposure categories*, not individuals.
- Nothing is stored; reports are generated locally.

## Features

| Feature | Where |
|---|---|
| 20 categories x 2 questions (profile visibility, location, MFA, password reuse, social engineering, ...) | `privacy_framework/questions.py` |
| Weighted scoring + risky-combination bonus | `privacy_framework/scoring.py` |
| Recommendations + checklist | `privacy_framework/recommendations.py` |
| Markdown / HTML report | `privacy_framework/report.py` |
| Security-awareness guidance | `privacy_framework/awareness.py` |
| Synthetic population (300 fictional profiles) | `privacy_framework/synthetic.py` |
| Web app + aggregate dashboard | `app.py` (Streamlit) |
| Command-line version | `cli.py` |
| Unit tests | `tests/` |
| One-command runner | `run_all.py` |

## Quick start (beginner friendly)

1. Install Python 3.10+ and open a terminal in this folder.
2. (Recommended) create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```
3. Run everything:
   ```
   python run_all.py --install
   ```
   This installs requirements, runs tests, generates the synthetic dataset, writes a sample report to `reports/`, and opens the web app.

Other commands:

```
python run_all.py --no-ui                    # everything except the web app
python -m streamlit run app.py               # web app only
python cli.py --demo --archetype oversharer  # CLI with a fictional persona
python cli.py --interactive                  # answer questions in the terminal
python -m unittest discover -s tests -v      # tests only
```

## How scoring works

1. Every answer option has a risk value from 0 (safest) to 100 (most exposed).
2. **Category score** = average risk of the category's questions.
3. **Base score** = weighted average of category scores. Authentication, MFA, password reuse, location and social engineering have higher weights.
4. **Combination bonus** (max +15) when two risky habits reinforce each other, e.g. no MFA + reused passwords.
5. **Overall** = `min(100, round(base + bonus))`.

| Score | Level |
|---|---|
| 0-20 | LOW |
| 21-40 | MODERATE |
| 41-70 | HIGH |
| 71-100 | CRITICAL |

A question is reported as a **weakness** when its answer risk is 50 or more (High severity at 75+). The checklist marks an item done when its answer risk is below 40.

## Project structure

```
privacy-risk-framework/
├── app.py                  # Streamlit UI + dashboard
├── cli.py                  # command-line interface
├── run_all.py              # run tests, data, report, UI
├── requirements.txt
├── privacy_framework/      # core logic (no UI code)
├── tests/                  # unit tests
├── data/                   # synthetic dataset (generated)
├── reports/                # sample reports (generated)
└── docs/PROOF_OF_WORK.md   # GitHub + LinkedIn guide
```

## Limitations

- Self-reported answers; the tool cannot verify real settings.
- Weights and risk values are expert-judgement defaults, not statistically validated.
- Platform settings change; recommendations are generic, not platform-specific.
- Synthetic dashboard data shows how the dashboard works, not real-world statistics.

## Ideas for future work

- Platform-specific checklists
- Score history and progress tracking (local only)
- Configurable weights via a JSON file
- Exportable PDF report
- Mapping questions to a recognised framework (e.g. NIST Privacy Framework)

## License

MIT (add a `LICENSE` file when you publish).
