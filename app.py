from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from features import explain_message, normalize_text, safety_advice, structural_features  # noqa: E402
from train_model import MODEL_PATH, METRICS_PATH, train  # noqa: E402
from plot_assets import ASSET_DIR, generate_plot_assets  # noqa: E402

st.set_page_config(
    page_title="SMS Scam Detector | CGIS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
:root {
  --navy: #0f172a;
  --slate: #475569;
  --muted: #64748b;
  --line: #e2e8f0;
  --bg: #f8fafc;
  --green: #16a34a;
  --amber: #f59e0b;
  --red: #dc2626;
  --blue: #2563eb;
  --purple: #7c3aed;
}
.block-container {
  padding-top: 1.25rem;
  padding-bottom: 2.5rem;
  max-width: 1320px;
}
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at top right, rgba(37,99,235,.12), transparent 28rem),
    radial-gradient(circle at 0% 20%, rgba(22,163,74,.10), transparent 22rem),
    #f8fafc;
}
.hero {
  border-radius: 28px;
  padding: 1.55rem 1.65rem;
  margin-bottom: 1.1rem;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 58%, #166534 100%);
  color: white;
  box-shadow: 0 20px 50px rgba(15, 23, 42, .18);
  position: relative;
  overflow: hidden;
}
.hero:after {
  content: "";
  position: absolute;
  width: 16rem;
  height: 16rem;
  border-radius: 999px;
  background: rgba(252, 209, 22, .18);
  right: -5rem;
  top: -6rem;
}
.hero h1 { font-size: clamp(2rem, 4vw, 3.7rem); line-height: 1.02; margin: 0 0 .45rem 0; font-weight: 850; letter-spacing: -.04em; }
.hero p { font-size: 1.04rem; color: rgba(255,255,255,.86); max-width: 850px; margin: .15rem 0; }
.hero .tag { display: inline-block; padding: .35rem .65rem; border: 1px solid rgba(255,255,255,.25); border-radius: 999px; background: rgba(255,255,255,.12); font-size: .82rem; margin-bottom: .8rem; }
.panel, .metric-card, .result-card, .indicator-card, .sample-card {
  background: rgba(255,255,255,.88);
  border: 1px solid rgba(226,232,240,.95);
  border-radius: 22px;
  box-shadow: 0 10px 30px rgba(15,23,42,.06);
}
.panel { padding: 1.1rem; }
.metric-card { padding: .95rem 1rem; min-height: 105px; }
.metric-card .value { font-size: 1.7rem; font-weight: 850; color: var(--navy); line-height: 1; }
.metric-card .label { margin-top: .38rem; color: var(--muted); font-size: .82rem; }
.metric-card .hint { margin-top: .3rem; color: #94a3b8; font-size: .74rem; }
.result-card { padding: 1.15rem 1.25rem; border-left: 10px solid var(--blue); }
.result-card.ham { border-left-color: var(--green); }
.result-card.spam { border-left-color: var(--amber); }
.result-card.smishing { border-left-color: var(--red); }
.result-title { font-size: clamp(1.35rem, 2.2vw, 2.1rem); color: var(--navy); margin: 0; font-weight: 850; }
.result-subtitle { color: var(--slate); margin-top: .25rem; }
.confidence-pill { display:inline-flex; align-items:center; gap:.35rem; border-radius:999px; padding:.42rem .7rem; font-weight:800; background:#eff6ff; color:#1d4ed8; margin-top:.7rem; }
.risk-bar-wrap { height: 12px; border-radius: 999px; background: #e2e8f0; overflow: hidden; margin: .65rem 0 .2rem; }
.risk-bar { height: 100%; border-radius: 999px; }
.indicator-card { padding: .85rem .95rem; margin-bottom: .65rem; }
.indicator-head { display:flex; align-items:center; justify-content:space-between; gap: .6rem; }
.indicator-title { color: var(--navy); font-weight: 800; }
.indicator-detail { color: var(--slate); font-size:.9rem; margin-top:.28rem; }
.badge { border-radius:999px; padding:.22rem .5rem; font-size:.72rem; font-weight:850; white-space:nowrap; }
.badge-high { background:#fee2e2; color:#991b1b; }
.badge-medium { background:#fef3c7; color:#92400e; }
.badge-low { background:#dcfce7; color:#166534; }
.section-title { color: var(--navy); font-weight: 850; letter-spacing: -.02em; margin: .2rem 0 .7rem; font-size: 1.2rem; }
.small-muted { color: var(--muted); font-size:.9rem; }
.stTextArea textarea {
  border-radius: 30px !important;
  border: 1px solid #cbd5e1 !important;
  box-shadow: 0 8px 20px rgba(15,23,42,.04) !important;
  font-size: 1rem !important;
}
.stButton button, .stDownloadButton button {
  border-radius: 14px !important;
  min-height: 2.8rem;
  font-weight: 800 !important;
}
div[data-testid="stMetric"] {
  background: white;
  padding: .85rem;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
}
.sample-card { padding:.75rem .85rem; margin-bottom:.55rem; cursor: default; }
.sample-card b { color: var(--navy); }
.sample-card span { color: var(--muted); font-size:.83rem; }
.cameroon-bar { display:flex; height:6px; overflow:hidden; border-radius:999px; margin-bottom:.75rem; }
.cameroon-bar div:nth-child(1){background:#007a3d; flex:1}.cameroon-bar div:nth-child(2){background:#ce1126; flex:1}.cameroon-bar div:nth-child(3){background:#fcd116; flex:1}
@media (max-width: 900px) {
  .hero { padding: 1.15rem; border-radius: 22px; }
  .panel { padding: .85rem; }
  .metric-card { min-height: 88px; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

LABEL_META = {
    "ham": {"title": "Safe / Ham", "emoji": "✅", "class": "ham", "risk": 12, "color": "#16a34a"},
    "spam": {"title": "Spam / Promotional", "emoji": "⚠️", "class": "spam", "risk": 48, "color": "#f59e0b"},
    "smishing": {"title": "Smishing / Scam", "emoji": "🚨", "class": "smishing", "risk": 92, "color": "#dc2626"},
}

SAMPLES = {
    "Safe family message": "Hi mum, I will be home by 6pm. Please keep dinner for me.",
    "Promotional spam": "FREE airtime for all users this weekend. Text YES to 8080 for promo details.",
    "Orange Money scam": "Orange Money account blocked. Verify immediately: https://om-secure-login.com",
    "French banking scam": "Votre compte bancaire sera suspendu. Confirmez vos informations ici: http://banque-verif.net",
    "MTN MoMo PIN scam": "MTN MoMo: Suspicious login detected. Send your PIN to 699000111 to secure account.",
}


def inject_hero() -> None:
    st.markdown(
        """
        <div class="hero">
          <span class="tag">CGIS · Yaoundé Girls in STEAM Hackathon · Explainable AI</span>
          <h1>SMS Scam Detector</h1>
          <p><b>Detect suspicious SMS before users click, pay, or share secrets.</b></p>
          <p>AI-powered smishing classification with confidence scores, local Cameroon examples, and human-readable risk explanations.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        train()
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_metrics():
    if not METRICS_PATH.exists():
        train()
    try:
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


@st.cache_data
def asset_paths():
    expected = [
        ASSET_DIR / "label_distribution.png",
        ASSET_DIR / "risk_signal_prevalence.png",
        ASSET_DIR / "confusion_matrix.png",
        ASSET_DIR / "metrics_summary.png",
        ASSET_DIR / "feature_profile.png",
        ASSET_DIR / "risk_indicators.png",
    ]
    if not all(p.exists() for p in expected):
        try:
            generate_plot_assets()
        except Exception:
            pass
    return {p.stem: p for p in expected if p.exists()}


def predict_sms(model, message: str):
    cleaned = normalize_text(message)
    pred = model.predict([cleaned])[0]
    confidence = None
    probs = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba([cleaned])[0]
        classes = list(model.classes_)
        probs = dict(zip(classes, proba))
        confidence = float(max(proba))
    return pred, confidence, probs


def metric_card(value: str, label: str, hint: str = ""):
    st.markdown(f"""
    <div class="metric-card">
      <div class="value">{value}</div>
      <div class="label">{label}</div>
      <div class="hint">{hint}</div>
    </div>
    """, unsafe_allow_html=True)


def render_result(pred: str, confidence: float | None):
    meta = LABEL_META.get(pred, {"title": pred.title(), "emoji": "ℹ️", "class": "spam", "risk": 50, "color": "#2563eb"})
    conf_txt = f"{confidence:.0%}" if confidence is not None else "N/A"
    st.markdown(f"""
    <div class="result-card {meta['class']}">
      <p class="result-title">{meta['emoji']} {meta['title']}</p>
      <div class="result-subtitle">Recommended action: {safety_advice(pred)}</div>
      <span class="confidence-pill">Confidence · {conf_txt}</span>
      <div class="risk-bar-wrap"><div class="risk-bar" style="width:{meta['risk']}%; background:{meta['color']};"></div></div>
      <div class="small-muted">Estimated user-facing risk level</div>
    </div>
    """, unsafe_allow_html=True)


def render_indicator(ind):
    st.markdown(f"""
    <div class="indicator-card">
      <div class="indicator-head">
        <div class="indicator-title">{ind.label}</div>
        <span class="badge badge-{ind.severity}">{ind.severity.upper()}</span>
      </div>
      <div class="indicator-detail">{ind.detail}</div>
    </div>
    """, unsafe_allow_html=True)


with st.sidebar:
    st.markdown('<div class="cameroon-bar"><div></div><div></div><div></div></div>', unsafe_allow_html=True)
    st.header("Demo controls")
    sample_name = st.selectbox("Sample SMS", list(SAMPLES.keys()))
    two_class = st.toggle("Pitch mode: safe vs scam", value=False, help="Maps smishing to scam and ham/spam to safer/non-scam for a simpler user story.")
    st.divider()
    st.subheader("Quick samples")
    for name, text in SAMPLES.items():
        st.markdown(f"<div class='sample-card'><b>{name}</b><br><span>{text[:82]}...</span></div>", unsafe_allow_html=True)
    st.divider()
    if st.button("Retrain model + refresh plots", type="primary", use_container_width=True):
        with st.spinner("Training model and regenerating analytics assets..."):
            train()
            generate_plot_assets()
            st.cache_resource.clear()
            st.cache_data.clear()
        st.success("Model, metrics, and plots refreshed.")
    st.download_button(
        "Download dataset",
        data=(ROOT / "data" / "sample_sms.csv").read_text(encoding="utf-8"),
        file_name="sample_sms.csv",
        mime="text/csv",
        use_container_width=True,
    )

inject_hero()
model = load_model()
metrics = load_metrics()
assets = asset_paths()

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card(f"{metrics.get('accuracy', 0):.0%}", "Accuracy", "latest saved model")
with m2:
    metric_card(f"{metrics.get('precision_macro', 0):.0%}", "Macro precision", "balanced class view")
with m3:
    metric_card(f"{metrics.get('recall_macro', 0):.0%}", "Macro recall", "optimize scam recall")
with m4:
    metric_card(str(metrics.get("n_samples", "—")), "Training SMS", "current dataset size")

st.write("")
left, right = st.columns([1.12, 0.88], gap="large")
with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Analyze a message</div>', unsafe_allow_html=True)
    message = st.text_area(
        "SMS text",
        value=SAMPLES[sample_name],
        height=155,
        label_visibility="collapsed",
        placeholder="Paste a message such as: Your account is blocked. Click this link to verify...",
    )
    c1, c2 = st.columns([1, 1])
    with c1:
        analyze = st.button("Analyze SMS", type="primary", use_container_width=True)
    with c2:
        clear_demo = st.button("Use selected sample", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Demo promise</div>', unsafe_allow_html=True)
    st.markdown(
        """
        **What the jury sees in under 60 seconds:**
        - prediction class;
        - confidence score;
        - risk explanations;
        - safety advice;
        - Cameroon-relevant examples.
        """
    )
    st.info("Tip: use the Orange Money or MTN MoMo sample during the live demo.")
    st.markdown('</div>', unsafe_allow_html=True)

if message:
    pred, confidence, probs = predict_sms(model, message)
    if two_class:
        st.caption(f"Pitch-mode mapping: model predicted **{pred}** → user-facing class **{'scam' if pred == 'smishing' else 'safe/non-scam'}**")

    st.write("")
    res_col, why_col = st.columns([1.05, 0.95], gap="large")
    with res_col:
        render_result(pred, confidence)
        if probs:
            st.markdown('<div class="panel" style="margin-top: .9rem;">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Class probabilities</div>', unsafe_allow_html=True)
            prob_df = pd.DataFrame({"class": list(probs.keys()), "probability": list(probs.values())}).sort_values("probability", ascending=False)
            st.bar_chart(prob_df.set_index("class"), height=230)
            st.markdown('</div>', unsafe_allow_html=True)
    with why_col:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Why this was flagged</div>', unsafe_allow_html=True)
        for indicator in explain_message(message):
            render_indicator(indicator)
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("Technical structural features detected"):
        feat = structural_features(message)
        st.dataframe(pd.DataFrame([feat]).T.rename(columns={0: "value"}), use_container_width=True)

st.write("")
st.markdown('<div class="section-title">Latest training analytics</div>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["Dataset", "Signals", "Model evaluation"])
with tab1:
    a, b = st.columns(2)
    with a:
        if "label_distribution" in assets:
            st.image(str(assets["label_distribution"]), use_container_width=True)
    with b:
        if "feature_profile" in assets:
            st.image(str(assets["feature_profile"]), use_container_width=True)
with tab2:
    a, b = st.columns(2)
    with a:
        if "risk_signal_prevalence" in assets:
            st.image(str(assets["risk_signal_prevalence"]), use_container_width=True)
    with b:
        if "risk_indicators" in assets:
            st.image(str(assets["risk_indicators"]), use_container_width=True)
with tab3:
    a, b = st.columns(2)
    with a:
        if "metrics_summary" in assets:
            st.image(str(assets["metrics_summary"]), use_container_width=True)
    with b:
        if "confusion_matrix" in assets:
            st.image(str(assets["confusion_matrix"]), use_container_width=True)

st.caption("Prototype note: replace the sample dataset with a larger verified dataset, retrain, and the app + PowerPoint assets will automatically reflect the latest plots.")
