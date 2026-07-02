"""Feature extraction and explanation helpers for SMS scam detection."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

URL_RE = re.compile(r"(?i)\b(?:https?://|www\.|bit\.ly/|tinyurl\.com/|t\.co/|[a-z0-9-]+\.(?:com|net|org|cm|info|biz)\b)")
EMAIL_RE = re.compile(r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b")
PHONE_RE = re.compile(r"(?:(?:\+?237)?\s?(?:6\d{2}|2\d{2})[\s.-]?\d{3}[\s.-]?\d{3}|\b\d{4,}\b)")
MONEY_RE = re.compile(r"(?i)(?:xaf|fcfa|cfa|\$|€|money|argent|paiement|payment|momo|orange money|mobile money)")
OTP_PIN_RE = re.compile(r"(?i)\b(?:pin|otp|password|mot de passe|code secret|login|identifiant|card details|bank login)\b")
URGENCY_RE = re.compile(r"(?i)\b(?:urgent|immediately|now|today|within|blocked|suspended|expires|alert|security|verify|confirm|update|cancel|débloquer|suspendu|confirmez|immédiatement|alerte|maintenant)\b")
REWARD_RE = re.compile(r"(?i)\b(?:won|winner|congratulations|selected|prize|bonus|free|grant|refund|double your money|gagné|félicitations|cadeau|remboursement|gratuit)\b")
THREAT_RE = re.compile(r"(?i)\b(?:blocked|suspended|accident|hospital|failed|expires|suspicious|unknown device|bloqué|suspendu|accident|hôpital|échoué)\b")
ACTION_RE = re.compile(r"(?i)\b(?:click|call|reply|send|dial|visit|register|enter|provide|verify|confirm|update|cliquez|appelez|répondez|envoyez|confirmez|entrez)\b")

SUSPICIOUS_KEYWORDS = [
    "urgent", "verify", "blocked", "suspended", "winner", "prize", "free", "refund", "otp", "pin",
    "password", "login", "account", "bank", "momo", "orange money", "mobile money", "pay", "payment",
    "accident", "hospital", "grant", "selected", "confirm", "update", "click", "bit.ly", "http",
    "urgent", "vérifier", "bloqué", "suspendu", "gratuit", "cadeau", "remboursement", "compte",
    "banque", "confirmez", "cliquez", "argent", "paiement",
]


def normalize_text(text: str) -> str:
    """Light normalization that preserves phishing signals such as URLs and phone numbers."""
    if text is None:
        return ""
    text = str(text).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def structural_features(text: str) -> Dict[str, float]:
    raw = "" if text is None else str(text)
    lower = normalize_text(raw)
    suspicious_count = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in lower)
    words = re.findall(r"\w+", lower, flags=re.UNICODE)
    return {
        "has_url": float(bool(URL_RE.search(raw))),
        "has_email": float(bool(EMAIL_RE.search(raw))),
        "has_phone": float(bool(PHONE_RE.search(raw))),
        "has_money": float(bool(MONEY_RE.search(raw))),
        "has_otp_pin": float(bool(OTP_PIN_RE.search(raw))),
        "urgency_count": float(len(URGENCY_RE.findall(raw))),
        "reward_count": float(len(REWARD_RE.findall(raw))),
        "threat_count": float(len(THREAT_RE.findall(raw))),
        "action_count": float(len(ACTION_RE.findall(raw))),
        "suspicious_keyword_count": float(suspicious_count),
        "char_len": float(len(raw)),
        "word_count": float(len(words)),
        "exclamation_count": float(raw.count("!")),
        "question_count": float(raw.count("?")),
        "digit_count": float(sum(ch.isdigit() for ch in raw)),
        "uppercase_ratio": float(sum(ch.isupper() for ch in raw) / max(1, sum(ch.isalpha() for ch in raw))),
    }


class SmsFeatureExtractor(BaseEstimator, TransformerMixin):
    """sklearn transformer that converts SMS text into numeric structural features."""

    feature_names = [
        "has_url", "has_email", "has_phone", "has_money", "has_otp_pin", "urgency_count", "reward_count",
        "threat_count", "action_count", "suspicious_keyword_count", "char_len", "word_count",
        "exclamation_count", "question_count", "digit_count", "uppercase_ratio",
    ]

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if isinstance(X, pd.DataFrame):
            values = X.iloc[:, 0].tolist()
        elif isinstance(X, pd.Series):
            values = X.tolist()
        else:
            values = list(X)
        rows = [[structural_features(text)[name] for name in self.feature_names] for text in values]
        return np.asarray(rows, dtype=float)

    def get_feature_names_out(self, input_features=None):
        return np.asarray([f"struct__{name}" for name in self.feature_names], dtype=object)


@dataclass
class RiskIndicator:
    label: str
    severity: str
    detail: str


def explain_message(text: str) -> List[RiskIndicator]:
    """Rule-based human explanation of risky cues in an SMS."""
    indicators: List[RiskIndicator] = []
    raw = "" if text is None else str(text)

    def add(condition: bool, label: str, severity: str, detail: str) -> None:
        if condition:
            indicators.append(RiskIndicator(label, severity, detail))

    add(bool(URL_RE.search(raw)), "Contains a link", "high", "Scam SMS often push users to fake login or payment pages.")
    add(bool(PHONE_RE.search(raw)), "Contains a phone number", "medium", "Fraudsters may ask victims to call or send mobile money.")
    add(bool(EMAIL_RE.search(raw)), "Contains an email address", "low", "Email contact details can be part of a phishing workflow.")
    add(bool(OTP_PIN_RE.search(raw)), "Requests secret credentials", "high", "Legitimate services should not ask for PIN, OTP, password, or card details by SMS.")
    add(bool(URGENCY_RE.search(raw)), "Uses urgency or account-pressure language", "high", "Urgent deadlines reduce careful checking and are common in smishing.")
    add(bool(REWARD_RE.search(raw)), "Promises a reward or free offer", "medium", "Unexpected prizes, grants, refunds, or free offers are common bait.")
    add(bool(THREAT_RE.search(raw)), "Uses threat or fear language", "high", "Warnings about blocked accounts, accidents, or failed payments can manipulate users.")
    add(bool(MONEY_RE.search(raw)), "Mentions money or mobile money", "medium", "Financial wording increases risk when combined with links, PINs, or urgency.")
    add(raw.count("!") >= 2, "Multiple exclamation marks", "low", "Aggressive punctuation is often used in mass spam or scam messages.")

    if not indicators:
        indicators.append(RiskIndicator("No obvious scam cues found", "low", "The message lacks common phishing signals, but users should still verify unusual requests."))
    return indicators


def safety_advice(prediction: str) -> str:
    if prediction == "smishing":
        return "Do not click links, do not share OTP/PIN/passwords, and verify through the official app, branch, or known customer-care number."
    if prediction == "spam":
        return "Treat as promotional or unsolicited. Avoid replying if you do not recognize the sender."
    return "Looks low-risk, but still be careful with unexpected requests for money, passwords, or verification codes."
