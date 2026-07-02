"""Train the SMS scam detector model and save artifacts."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from features import SmsFeatureExtractor, normalize_text
from plot_assets import generate_plot_assets

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "sample_sms.csv"
MODEL_PATH = ROOT / "models" / "sms_detector.joblib"
METRICS_PATH = ROOT / "models" / "metrics.json"


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.dropna(subset=["text", "label"]).copy()
    df["text"] = df["text"].map(normalize_text)
    return df


def build_pipeline() -> Pipeline:
    text_features = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True, strip_accents="unicode")),
    ])
    structural_features = Pipeline([
        ("extract", SmsFeatureExtractor()),
        ("scale", StandardScaler(with_mean=False)),
    ])
    features = FeatureUnion([
        ("text", text_features),
        ("struct", structural_features),
    ])
    return Pipeline([
        ("features", features),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)),
    ])


def train() -> dict:
    df = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.25, random_state=42, stratify=df["label"]
    )
    model = build_pipeline()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    labels = sorted(df["label"].unique())
    metrics = {
        "data_path": str(DATA_PATH),
        "n_samples": int(len(df)),
        "labels": labels,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision_macro": float(precision_score(y_test, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_test, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
        "classification_report": classification_report(y_test, y_pred, zero_division=0, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=labels).tolist(),
        "confusion_matrix_labels": labels,
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    # Generate fresh analytics images for the app and PowerPoint deck.
    try:
        metrics["plot_assets"] = generate_plot_assets(DATA_PATH, METRICS_PATH)
        METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    except Exception as exc:  # plotting should never break training
        metrics["plot_asset_error"] = str(exc)

    return metrics


if __name__ == "__main__":
    metrics = train()
    print(json.dumps(metrics, indent=2))
