"""Generate analytics image assets from the latest dataset and model metrics.

These images are used by the Streamlit app and the PowerPoint deck.
Run automatically from train_model.py, or manually:
    python src/plot_assets.py
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable

import matplotlib.pyplot as plt
import pandas as pd

from features import structural_features

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "sample_sms.csv"
METRICS_PATH = ROOT / "models" / "metrics.json"
ASSET_DIR = ROOT / "docs" / "assets"

COLORS = {
    "ham": "#16a34a",
    "spam": "#f59e0b",
    "smishing": "#dc2626",
    "safe": "#16a34a",
    "scam": "#dc2626",
}


def _savefig(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=220, facecolor="white", bbox_inches="tight")
    plt.close()


def _load_metrics(metrics_path: Path = METRICS_PATH) -> Dict:
    if metrics_path.exists():
        return json.loads(metrics_path.read_text(encoding="utf-8"))
    return {}


def generate_plot_assets(
    data_path: Path = DATA_PATH,
    metrics_path: Path = METRICS_PATH,
    asset_dir: Path = ASSET_DIR,
) -> Dict[str, str]:
    """Create plot PNG files and return their paths as strings."""
    asset_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(data_path)
    metrics = _load_metrics(metrics_path)

    features = pd.DataFrame([structural_features(text) for text in df["text"]])
    analytics = pd.concat([df[["label"]], features], axis=1)

    paths = {
        "label_distribution": asset_dir / "label_distribution.png",
        "risk_signal_prevalence": asset_dir / "risk_signal_prevalence.png",
        "confusion_matrix": asset_dir / "confusion_matrix.png",
        "risk_indicators": asset_dir / "risk_indicators.png",
        "metrics_summary": asset_dir / "metrics_summary.png",
        "feature_profile": asset_dir / "feature_profile.png",
    }

    # 1) Label distribution
    label_order = [x for x in ["ham", "spam", "smishing"] if x in set(df["label"])]
    label_order += [x for x in sorted(df["label"].unique()) if x not in label_order]
    counts = df["label"].value_counts().reindex(label_order).fillna(0)
    plt.figure(figsize=(7.2, 4.2))
    bars = plt.bar(counts.index, counts.values, color=[COLORS.get(x, "#2563eb") for x in counts.index])
    plt.title("Latest Training Dataset: Label Distribution", fontsize=14, fontweight="bold")
    plt.ylabel("Number of SMS")
    plt.grid(axis="y", alpha=0.25)
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, str(int(bar.get_height())), ha="center", fontsize=11, fontweight="bold")
    _savefig(paths["label_distribution"])

    # 2) Risk signal prevalence by class
    signal_cols = ["has_url", "has_phone", "has_money", "has_otp_pin", "has_email"]
    available = [c for c in signal_cols if c in analytics.columns]
    prevalence = analytics.groupby("label")[available].mean().reindex(label_order).fillna(0) * 100
    plt.figure(figsize=(8.2, 4.6))
    prevalence.T.plot(kind="bar", color=[COLORS.get(c, "#2563eb") for c in prevalence.index], ax=plt.gca())
    plt.title("Risk Signal Prevalence by Class", fontsize=14, fontweight="bold")
    plt.ylabel("% of messages")
    plt.xticks(rotation=25, ha="right")
    plt.ylim(0, 105)
    plt.grid(axis="y", alpha=0.25)
    plt.legend(title="Class", frameon=False)
    _savefig(paths["risk_signal_prevalence"])

    # 3) Confusion matrix
    cm = metrics.get("confusion_matrix")
    cm_labels = metrics.get("confusion_matrix_labels")
    if cm and cm_labels:
        plt.figure(figsize=(5.4, 4.5))
        plt.imshow(cm, cmap="Blues")
        plt.title("Latest Model Confusion Matrix", fontsize=14, fontweight="bold")
        plt.xticks(range(len(cm_labels)), cm_labels, rotation=25)
        plt.yticks(range(len(cm_labels)), cm_labels)
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        max_val = max(max(row) for row in cm) if cm else 1
        for i, row in enumerate(cm):
            for j, val in enumerate(row):
                plt.text(j, i, str(val), ha="center", va="center", fontsize=13, fontweight="bold", color="white" if val > max_val/2 else "#0f172a")
        plt.colorbar(fraction=0.046, pad=0.04)
        _savefig(paths["confusion_matrix"])

    # 4) Explainability risk indicators chart
    risk_items = pd.Series({
        "URL/link": 100,
        "Urgency": 92,
        "PIN/OTP request": 88,
        "Money context": 75,
        "Phone number": 60,
        "Reward bait": 45,
    })
    plt.figure(figsize=(7.2, 4.2))
    colors = ["#dc2626", "#dc2626", "#ef4444", "#f59e0b", "#f59e0b", "#84cc16"]
    plt.barh(risk_items.index[::-1], risk_items.values[::-1], color=colors[::-1])
    plt.xlim(0, 100)
    plt.title("Explainable Risk Indicators Used by the App", fontsize=14, fontweight="bold")
    plt.xlabel("Relative risk weight for explanation")
    plt.grid(axis="x", alpha=0.25)
    for y, val in enumerate(risk_items.values[::-1]):
        plt.text(val + 1, y, f"{val}%", va="center", fontsize=10, fontweight="bold")
    _savefig(paths["risk_indicators"])

    # 5) Metrics summary
    metric_names = ["accuracy", "precision_macro", "recall_macro", "f1_macro"]
    metric_labels = ["Accuracy", "Precision", "Recall", "F1"]
    vals = [float(metrics.get(name, 0)) * 100 for name in metric_names]
    plt.figure(figsize=(7.2, 4.2))
    bars = plt.bar(metric_labels, vals, color=["#2563eb", "#16a34a", "#f59e0b", "#7c3aed"])
    plt.title("Latest Model Evaluation Summary", fontsize=14, fontweight="bold")
    plt.ylabel("Score (%)")
    plt.ylim(0, 105)
    plt.grid(axis="y", alpha=0.25)
    for bar, val in zip(bars, vals):
        plt.text(bar.get_x() + bar.get_width()/2, val + 1, f"{val:.0f}%", ha="center", fontsize=11, fontweight="bold")
    _savefig(paths["metrics_summary"])

    # 6) Mean feature profile
    profile_cols = ["urgency_count", "reward_count", "threat_count", "action_count", "suspicious_keyword_count", "digit_count"]
    profile_cols = [c for c in profile_cols if c in analytics.columns]
    profile = analytics.groupby("label")[profile_cols].mean().reindex(label_order).fillna(0)
    plt.figure(figsize=(8.2, 4.6))
    profile.T.plot(kind="bar", color=[COLORS.get(c, "#2563eb") for c in profile.index], ax=plt.gca())
    plt.title("Average Structural Feature Profile", fontsize=14, fontweight="bold")
    plt.ylabel("Average count per SMS")
    plt.xticks(rotation=25, ha="right")
    plt.grid(axis="y", alpha=0.25)
    plt.legend(title="Class", frameon=False)
    _savefig(paths["feature_profile"])

    return {name: str(path) for name, path in paths.items() if path.exists()}


if __name__ == "__main__":
    created = generate_plot_assets()
    print(json.dumps(created, indent=2))
