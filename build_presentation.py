#!/usr/bin/env python3
"""One-command build for the CGIS presentation.

Run from the project folder:
    python build_presentation.py

Or retrain first:
    python build_presentation.py --retrain
"""
from __future__ import annotations

import argparse
import json
import runpy
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DOCS = ROOT / "docs"
METRICS = ROOT / "models" / "metrics.json"
WINNING_DECK = DOCS / "CGIS_SMS_Scam_Detector_Winning_Bilingual.pptx"
LEGACY_DECK = DOCS / "CGIS_SMS_Scam_Detector_Presentation.pptx"
DECK_SCRIPT = DOCS / "make_winning_bilingual_deck.py"

sys.path.insert(0, str(SRC))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--retrain", action="store_true", help="Retrain model before rebuilding PowerPoint.")
    args = parser.parse_args()

    from plot_assets import generate_plot_assets

    if args.retrain or not METRICS.exists():
        from train_model import train
        print("Training model...")
        train()
    else:
        print("Using existing model metrics. Add --retrain to train again.")

    print("Refreshing plot assets...")
    generate_plot_assets()

    print("Building bilingual PowerPoint from latest assets...")
    runpy.run_path(str(DECK_SCRIPT), run_name="__main__")
    shutil.copy2(WINNING_DECK, LEGACY_DECK)

    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    print("\nDone.")
    print(f"Samples: {metrics.get('n_samples')}")
    print(f"Accuracy: {metrics.get('accuracy', 0):.2%}")
    print(f"F1 macro: {metrics.get('f1_macro', 0):.2%}")
    print(f"Deck: {WINNING_DECK}")
    print(f"Compatibility copy: {LEGACY_DECK}")


if __name__ == "__main__":
    main()
