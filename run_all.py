"""Run everything: tests -> synthetic data -> sample report -> web app.

  python run_all.py              full run, then launch the web app
  python run_all.py --no-ui      everything except the web app
  python run_all.py --install    install requirements first
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def step(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--install", action="store_true", help="pip install requirements.txt first")
    p.add_argument("--no-ui", action="store_true", help="skip launching Streamlit")
    args = p.parse_args()

    if args.install:
        step("1/5 Installing requirements")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                       cwd=ROOT, check=True)

    step("2/5 Running unit tests")
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT)
    if r.returncode != 0:
        sys.exit("Tests failed - fix them before continuing.")

    step("3/5 Generating synthetic dataset (300 fictional profiles)")
    from privacy_framework.synthetic import generate_profiles, write_csv
    rows = generate_profiles(300, seed=42)
    (ROOT / "data").mkdir(exist_ok=True)
    write_csv(rows, ROOT / "data" / "synthetic_profiles.csv")
    print(f"Wrote {len(rows)} rows to data/synthetic_profiles.csv")

    step("4/5 Creating sample reports from a fictional persona")
    subprocess.run([sys.executable, "cli.py", "--demo", "--archetype", "oversharer"],
                   cwd=ROOT, check=True)

    if args.no_ui:
        print("\nDone (UI skipped).")
        return

    step("5/5 Launching the web app (Ctrl+C to stop)")
    try:
        import streamlit  # noqa: F401
    except ImportError:
        sys.exit("Streamlit missing. Run: python run_all.py --install")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=ROOT)


if __name__ == "__main__":
    main()
