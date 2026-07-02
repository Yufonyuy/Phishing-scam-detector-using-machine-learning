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

# Brighter, premium dashboard warning colors
COLORS = {
    "ham": "#10b981",       # Emerald Green
    "spam": "#f59e0b",      # Amber Yellow
    "smishing": "#ef4444",  # Crimson Red
    "safe": "#10b981",
    "scam": "#ef4444",
}

def _style_axis(ax) -> None:
    """Helper to apply premium dark theme styling to Matplotlib axes."""
    ax.set_facecolor("#161e31")  # Slate-850 dark panel background
    ax.tick_params(colors='#cbd5e1', which='both', labelsize=10) # Light grey tick labels
    ax.xaxis.label.set_color('#f8fafc')
    ax.yaxis.label.set_color('#f8fafc')
    ax.title.set_color('#f8fafc')
    
    # Style spines (borders)
    for spine in ax.spines.values():
        spine.set_color('#334155')  # Slate-700 border
        spine.set_linewidth(1.0)

def _savefig(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=220, facecolor="#0b0f19", edgecolor="none", bbox_inches="tight")
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

    # Standard figure size for all charts: 8.0 x 4.5
    FIG_SIZE = (8.0, 4.5)

    # 1) Label distribution
    label_order = [x for x in ["ham", "spam", "smishing"] if x in set(df["label"])]
    label_order += [x for x in sorted(df["label"].unique()) if x not in label_order]
    counts = df["label"].value_counts().reindex(label_order).fillna(0)
    
    plt.figure(figsize=FIG_SIZE, facecolor="#0b0f19")
    ax = plt.gca()
    _style_axis(ax)
    
    bars = plt.bar(counts.index, counts.values, color=[COLORS.get(x, "#3b82f6") for x in counts.index], width=0.5)
    plt.title("Latest Training Dataset: Label Distribution", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("Number of SMS")
    plt.grid(axis="y", color="#334155", alpha=0.4, linestyle=":")
    
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2, 
            height + max(1, height * 0.02), 
            str(int(height)), 
            ha="center", 
            fontsize=10, 
            fontweight="bold", 
            color="#f8fafc"
        )
    _savefig(paths["label_distribution"])

    # 2) Risk signal prevalence by class
    signal_cols = ["has_url", "has_phone", "has_money", "has_otp_pin", "has_email"]
    available = [c for c in signal_cols if c in analytics.columns]
    prevalence = analytics.groupby("label")[available].mean().reindex(label_order).fillna(0) * 100
    
    plt.figure(figsize=FIG_SIZE, facecolor="#0b0f19")
    ax = plt.gca()
    _style_axis(ax)
    
    prevalence.T.plot(kind="bar", color=[COLORS.get(c, "#3b82f6") for c in prevalence.index], ax=ax)
    plt.title("Risk Signal Prevalence by Class", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("% of messages")
    plt.xticks(rotation=15, ha="right")
    plt.ylim(0, 105)
    plt.grid(axis="y", color="#334155", alpha=0.4, linestyle=":")
    plt.legend(title="Class", frameon=True, facecolor="#161e31", edgecolor="#334155", labelcolor="#f8fafc")
    _savefig(paths["risk_signal_prevalence"])

    # 3) Confusion matrix
    cm = metrics.get("confusion_matrix")
    cm_labels = metrics.get("confusion_matrix_labels")
    if cm and cm_labels:
        plt.figure(figsize=FIG_SIZE, facecolor="#0b0f19")
        ax = plt.gca()
        _style_axis(ax)
        
        # imshow remains square because aspect='equal' is default, but sits nicely in the 8.0x4.5 canvas
        im = ax.imshow(cm, cmap="Blues")
        plt.title("Latest Model Confusion Matrix", fontsize=12, fontweight="bold", pad=12)
        plt.xticks(range(len(cm_labels)), cm_labels, rotation=15)
        plt.yticks(range(len(cm_labels)), cm_labels)
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        
        max_val = max(max(row) for row in cm) if cm else 1
        for i, row in enumerate(cm):
            for j, val in enumerate(row):
                ax.text(
                    j, i, str(val), 
                    ha="center", va="center", 
                    fontsize=12, fontweight="bold", 
                    color="white" if val > max_val/2 else "#0b0f19"
                )
        
        # Style colorbar for dark theme
        cbar = plt.colorbar(im, fraction=0.046, pad=0.04)
        cbar.ax.yaxis.set_tick_params(color='#cbd5e1')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#cbd5e1')
        cbar.outline.set_edgecolor('#334155')
        
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
    
    plt.figure(figsize=FIG_SIZE, facecolor="#0b0f19")
    ax = plt.gca()
    _style_axis(ax)
    
    # Matching dashboard indicators
    colors = ["#ef4444", "#ef4444", "#f87171", "#f59e0b", "#f59e0b", "#10b981"]
    plt.barh(risk_items.index[::-1], risk_items.values[::-1], color=colors[::-1], height=0.55)
    plt.xlim(0, 105)
    plt.title("Explainable Risk Indicators Used by the App", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Relative risk weight for explanation")
    plt.grid(axis="x", color="#334155", alpha=0.4, linestyle=":")
    
    for y, val in enumerate(risk_items.values[::-1]):
        plt.text(val + 1.5, y, f"{val}%", va="center", fontsize=9, fontweight="bold", color="#f8fafc")
    _savefig(paths["risk_indicators"])

    # 5) Metrics summary
    metric_names = ["accuracy", "precision_macro", "recall_macro", "f1_macro"]
    metric_labels = ["Accuracy", "Precision", "Recall", "F1 Score"]
    vals = [float(metrics.get(name, 0)) * 100 for name in metric_names]
    
    plt.figure(figsize=FIG_SIZE, facecolor="#0b0f19")
    ax = plt.gca()
    _style_axis(ax)
    
    bars = plt.bar(metric_labels, vals, color=["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"], width=0.5)
    plt.title("Latest Model Evaluation Summary", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("Score (%)")
    plt.ylim(0, 105)
    plt.grid(axis="y", color="#334155", alpha=0.4, linestyle=":")
    
    for bar, val in zip(bars, vals):
        plt.text(
            bar.get_x() + bar.get_width()/2, 
            val + 1.5, 
            f"{val:.0f}%", 
            ha="center", 
            fontsize=10, 
            fontweight="bold", 
            color="#f8fafc"
        )
    _savefig(paths["metrics_summary"])

    # 6) Mean feature profile
    profile_cols = ["urgency_count", "reward_count", "threat_count", "action_count", "suspicious_keyword_count", "digit_count"]
    profile_cols = [c for c in profile_cols if c in analytics.columns]
    profile = analytics.groupby("label")[profile_cols].mean().reindex(label_order).fillna(0)
    
    plt.figure(figsize=FIG_SIZE, facecolor="#0b0f19")
    ax = plt.gca()
    _style_axis(ax)
    
    profile.T.plot(kind="bar", color=[COLORS.get(c, "#3b82f6") for c in profile.index], ax=ax)
    plt.title("Average Structural Feature Profile", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("Average count per SMS")
    plt.xticks(rotation=15, ha="right")
    plt.grid(axis="y", color="#334155", alpha=0.4, linestyle=":")
    plt.legend(title="Class", frameon=True, facecolor="#161e31", edgecolor="#334155", labelcolor="#f8fafc")
    _savefig(paths["feature_profile"])

    return {name: str(path) for name, path in paths.items() if path.exists()}


if __name__ == "__main__":
    created = generate_plot_assets()
    print(json.dumps(created, indent=2))
