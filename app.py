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

# Premium split-complementary cybersecurity dashboard CSS overrides
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;850&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

:root {
  --navy: #030712;
  --panel-bg: rgba(17, 24, 39, 0.75);
  --panel-border: rgba(255, 255, 255, 0.06);
  --accent-blue: #06b6d4;
  --accent-purple: #6366f1;
  --accent-green: #10b981;
  --accent-amber: #f59e0b;
  --accent-red: #f43f5e;
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
  --text-muted: #4b5563;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background-color: var(--navy) !important;
  color: var(--text-primary) !important;
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 90% 10%, rgba(99, 102, 241, 0.15), transparent 50rem),
    radial-gradient(circle at 10% 90%, rgba(6, 182, 212, 0.1), transparent 45rem),
    #030712 !important;
}

h1, h2, h3, h4, h5, h6, .result-title, .section-title {
  font-family: 'Outfit', sans-serif !important;
  font-weight: 700 !important;
  color: var(--text-primary) !important;
  letter-spacing: -0.02em !important;
}

.block-container {
  padding-top: 1.5rem !important;
  padding-bottom: 3rem !important;
  max-width: 1300px !important;
}

/* Custom styled Streamlit containers (st.container(border=True)) */
div[data-testid="stVerticalBlockBorder"] {
  background: var(--panel-bg) !important;
  border: 1px solid var(--panel-border) !important;
  border-radius: 16px !important;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4) !important;
  padding: 1.5rem !important;
  backdrop-filter: blur(16px) !important;
  margin-bottom: 1.25rem !important;
}

/* Metric Cards style override */
.metric-card {
  background: rgba(31, 41, 55, 0.4) !important;
  border: 1px solid var(--panel-border) !important;
  border-radius: 14px !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
  padding: 1.1rem 1.2rem !important;
  min-height: 105px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.metric-card:hover {
  transform: translateY(-2px);
  border-color: rgba(6, 182, 212, 0.4) !important;
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.15) !important;
}
.metric-card .value {
  font-size: 1.85rem;
  font-weight: 850;
  color: var(--text-primary);
  line-height: 1;
  font-family: 'Outfit', sans-serif;
}
.metric-card .label {
  margin-top: .4rem;
  color: var(--text-secondary);
  font-size: .85rem;
  font-weight: 600;
}
.metric-card .hint {
  margin-top: .25rem;
  color: var(--text-muted);
  font-size: .75rem;
}

/* Prediction Result Cards - Complementary Accents */
.result-card {
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
  margin-bottom: 1.2rem;
}
.result-card.ham {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(17, 24, 39, 0.9) 100%) !important;
  border: 1px solid rgba(16, 185, 129, 0.3) !important;
  border-left: 6px solid var(--accent-green) !important;
}
.result-card.spam {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.12) 0%, rgba(17, 24, 39, 0.9) 100%) !important;
  border: 1px solid rgba(245, 158, 11, 0.3) !important;
  border-left: 6px solid var(--accent-amber) !important;
}
.result-card.smishing {
  background: linear-gradient(135deg, rgba(244, 63, 94, 0.12) 0%, rgba(17, 24, 39, 0.9) 100%) !important;
  border: 1px solid rgba(244, 63, 94, 0.3) !important;
  border-left: 6px solid var(--accent-red) !important;
}
.result-title {
  font-size: clamp(1.4rem, 2.5vw, 2.2rem) !important;
  margin: 0 !important;
  font-weight: 800 !important;
  letter-spacing: -0.03em !important;
}
.result-card.ham .result-title { color: #34d399 !important; }
.result-card.spam .result-title { color: #fbbf24 !important; }
.result-card.smishing .result-title { color: #f43f5e !important; }

.result-subtitle {
  color: #e5e7eb;
  margin-top: .4rem;
  font-size: 1rem;
  line-height: 1.4;
}
.confidence-pill {
  display: inline-flex;
  align-items: center;
  gap: .35rem;
  border-radius: 999px;
  padding: .25rem .75rem;
  font-weight: 700;
  font-size: 0.8rem;
  background: rgba(6, 182, 212, 0.12);
  color: #22d3ee;
  margin-top: 0.8rem;
  border: 1px solid rgba(6, 182, 212, 0.2);
}
.risk-bar-wrap {
  height: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  overflow: hidden;
  margin: .8rem 0 .3rem;
}
.risk-bar {
  height: 100%;
  border-radius: 999px;
}

/* Indicators styling */
.indicator-card {
  padding: 0.9rem 1.1rem;
  margin-bottom: 0.7rem;
  border-radius: 12px;
  background: rgba(31, 41, 55, 0.35);
  border: 1px solid var(--panel-border);
  transition: all 0.2s ease;
}
.indicator-card:hover {
  border-color: rgba(255, 255, 255, 0.12);
  background: rgba(31, 41, 55, 0.5);
}
.indicator-title {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.95rem;
}
.indicator-detail {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin-top: 0.3rem;
  line-height: 1.4;
}
.badge {
  border-radius: 6px;
  padding: .15rem .5rem;
  font-size: .65rem;
  font-weight: 800;
  letter-spacing: 0.03em;
}
.badge-high { background: rgba(244, 63, 94, 0.15); color: #fda4af; border: 1px solid rgba(244, 63, 94, 0.3); }
.badge-medium { background: rgba(245, 158, 11, 0.15); color: #fde047; border: 1px solid rgba(245, 158, 11, 0.3); }
.badge-low { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }

/* Sections title */
.section-title {
  color: var(--text-primary) !important;
  font-weight: 700 !important;
  font-size: 1.25rem !important;
  margin-bottom: 0.95rem !important;
  border-left: 4px solid var(--accent-blue);
  padding-left: 0.65rem;
}

/* Hero component */
.hero {
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, #0b0f19 0%, #111827 60%, #1e1b4b 100%);
  color: white;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  position: relative;
  overflow: hidden;
  border: 1px solid var(--panel-border);
}
.hero h1 {
  font-size: clamp(2rem, 3.8vw, 2.8rem);
  line-height: 1.1;
  margin: 0 0 .5rem 0;
  font-weight: 850;
  letter-spacing: -.03em;
  background: linear-gradient(to right, #ffffff 30%, #e5e7eb 70%, #818cf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero p {
  font-size: 1rem;
  color: #9ca3af;
  max-width: 900px;
  margin: .25rem 0;
  line-height: 1.5;
}
.hero .tag {
  display: inline-block;
  padding: .25rem .65rem;
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 6px;
  background: rgba(99, 102, 241, 0.1);
  font-size: .75rem;
  font-weight: 700;
  color: #a5b4fc;
  margin-bottom: 0.9rem;
  letter-spacing: 0.03em;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
  background-color: #030712 !important;
  border-right: 1px solid rgba(255, 255, 255, 0.04) !important;
}
[data-testid="stSidebar"] [data-testid="stHeader"] {
  background-color: #030712 !important;
}

/* Sidebar Quick Samples */
[data-testid="stSidebar"] div.stButton > button {
  background-color: rgba(31, 41, 55, 0.3) !important;
  border: 1px solid rgba(255, 255, 255, 0.05) !important;
  color: #9ca3af !important;
  text-align: left !important;
  padding: 0.75rem 0.9rem !important;
  border-radius: 8px !important;
  font-size: 0.8rem !important;
  transition: all 0.2s ease !important;
  display: block !important;
  white-space: normal !important;
  line-height: 1.4 !important;
}
[data-testid="stSidebar"] div.stButton > button:hover {
  background-color: rgba(99, 102, 241, 0.08) !important;
  border-color: rgba(99, 102, 241, 0.3) !important;
  color: #ffffff !important;
}

/* Form inputs */
.stTextArea textarea {
  background-color: #0b0f19 !important;
  color: var(--text-primary) !important;
  border-radius: 10px !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
}
.stTextArea textarea:focus {
  border-color: var(--accent-blue) !important;
  box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2) !important;
}

/* Primary Button styling */
div.stButton button[kind="primary"] {
  background: linear-gradient(135deg, var(--accent-blue) 0%, #0891b2 100%) !important;
  border: none !important;
  color: #ffffff !important;
  box-shadow: 0 4px 14px rgba(6, 182, 212, 0.3) !important;
}
div.stButton button[kind="primary"]:hover {
  background: linear-gradient(135deg, #22d3ee 0%, var(--accent-blue) 100%) !important;
  box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4) !important;
}

/* Secondary Button override */
div.stButton button[kind="secondary"] {
  background-color: rgba(255, 255, 255, 0.03) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  color: var(--text-secondary) !important;
}
div.stButton button[kind="secondary"]:hover {
  background-color: rgba(255, 255, 255, 0.07) !important;
  border-color: rgba(255, 255, 255, 0.15) !important;
  color: white !important;
}

/* Tabs customization */
button[data-baseweb="tab"] {
  color: var(--text-secondary) !important;
  font-weight: 600 !important;
  border-bottom: 2px solid transparent !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
  color: var(--accent-blue) !important;
  border-bottom-color: var(--accent-blue) !important;
}

/* Hide defaults */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.cameroon-bar {
  display: flex;
  height: 4px;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 1.25rem;
}
.cameroon-bar div:nth-child(1) { background: #007a3d; flex: 1; }
.cameroon-bar div:nth-child(2) { background: #ce1126; flex: 1; }
.cameroon-bar div:nth-child(3) { background: #fcd116; flex: 1; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

LABEL_META = {
    "ham": {"title": "Safe / Ham", "emoji": "✅", "class": "ham", "risk": 12, "color": "#10b981"},
    "spam": {"title": "Spam / Promotional", "emoji": "⚠️", "class": "spam", "risk": 48, "color": "#f59e0b"},
    "smishing": {"title": "Smishing / Scam", "emoji": "🚨", "class": "smishing", "risk": 92, "color": "#ef4444"},
}

SAMPLES = {
    "Safe family message": "Hi mum, I will be home by 6pm. Please keep dinner for me.",
    "Promotional spam": "FREE airtime for all users this weekend. Text YES to 8080 for promo details.",
    "Orange Money scam": "Orange Money account blocked. Verify immediately: https://om-secure-login.com",
    "French banking scam": "Votre compte bancaire sera suspendu. Confirmez vos informations ici: http://banque-verif.net",
    "MTN MoMo PIN scam": "MTN MoMo: Suspicious login detected. Send your PIN to 699000111 to secure account.",
}

# State synchronization helper
if "sms_input" not in st.session_state:
    st.session_state.sms_input = SAMPLES["Safe family message"]
if "selected_sample_name" not in st.session_state:
    st.session_state.selected_sample_name = "Safe family message"

def on_selectbox_change():
    val = st.session_state.sample_selectbox_widget
    st.session_state.selected_sample_name = val
    st.session_state.sms_input = SAMPLES[val]


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


def metric_card(value: str, label: str, hint: str = "", border_color: str = "#3b82f6"):
    st.markdown(f"""
    <div class="metric-card" style="border-left: 5px solid {border_color} !important;">
      <div class="value">{value}</div>
      <div class="label">{label}</div>
      <div class="hint">{hint}</div>
    </div>
    """, unsafe_allow_html=True)


def render_result(pred: str, confidence: float | None):
    meta = LABEL_META.get(pred, {"title": pred.title(), "emoji": "ℹ️", "class": "spam", "risk": 50, "color": "#3b82f6"})
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
    
    sample_list = list(SAMPLES.keys())
    try:
        default_idx = sample_list.index(st.session_state.selected_sample_name)
    except ValueError:
        default_idx = 0
        
    sample_name = st.selectbox(
        "Sample SMS", 
        sample_list, 
        index=default_idx,
        key="sample_selectbox_widget",
        on_change=on_selectbox_change
    )
    
    two_class = st.toggle(
        "Pitch mode: safe vs scam", 
        value=False, 
        help="Maps smishing to scam and ham/spam to safer/non-scam for a simpler user story."
    )
    
    st.divider()
    st.subheader("Quick samples")
    
    for name, text in SAMPLES.items():
        preview = f"{text[:45]}..." if len(text) > 45 else text
        if st.button(
            f"📋 {name}\n{preview}", 
            key=f"sample_btn_{name}", 
            use_container_width=True
        ):
            st.session_state.sms_input = text
            st.session_state.selected_sample_name = name
            st.rerun()
            
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

# Metric Columns
# Metric Columns
m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card(f"{metrics.get('accuracy', 0):.0%}", "Accuracy", "latest saved model", "#3b82f6")
with m2:
    metric_card(f"{metrics.get('precision_macro', 0):.0%}", "Macro precision", "balanced class view", "#8b5cf6")
with m3:
    metric_card(f"{metrics.get('recall_macro', 0):.0%}", "Macro recall", "optimize scam recall", "#f59e0b")
with m4:
    metric_card(str(metrics.get("n_samples", "—")), "Training SMS", "current dataset size", "#10b981")

st.write("")

# --- NEW SIDE-BY-SIDE UPPER SECTION ---
def clear_sms_input():
    st.session_state.sms_input = ""
    st.session_state.selected_sample_name = ""

col1, col2 = st.columns([1.12, 0.88], gap="large")

with col1:
    with st.container(border=True):
        st.markdown('<div class="section-title">Analyze a message</div>', unsafe_allow_html=True)
        message = st.text_area(
            "SMS text",
            value=st.session_state.sms_input,
            height=155,
            label_visibility="collapsed",
            placeholder="Paste a message such as: Your account is blocked. Click this link to verify...",
            key="sms_input"
        )
        c1, c2 = st.columns([1, 1])
        with c1:
            analyze = st.button("Analyze SMS", type="primary", use_container_width=True)
        with c2:
            st.button("Clear Input", use_container_width=True, on_click=clear_sms_input)

with col2:
    with st.container(border=True):
        st.markdown('<div class="section-title">How to Use the Platform</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="indicator-card" style="border-left: 4px solid var(--accent-blue) !important; margin-bottom: 0.5rem;">
          <div class="indicator-head">
            <div class="indicator-title">1. Select or Paste Input</div>
            <span class="badge badge-low">STEP 01</span>
          </div>
          <div class="indicator-detail">Choose a local sample from the sidebar or paste custom SMS text.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="indicator-card" style="border-left: 4px solid var(--accent-purple) !important; margin-bottom: 0.5rem;">
          <div class="indicator-head">
            <div class="indicator-title">2. Run Vector Classification</div>
            <span class="badge badge-medium">STEP 02</span>
          </div>
          <div class="indicator-detail">Click <b>Analyze SMS</b> to calculate prediction weights and probabilities.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="indicator-card" style="border-left: 4px solid var(--accent-green) !important; margin-bottom: 0;">
          <div class="indicator-head">
            <div class="indicator-title">3. Evaluate Risk Metrics</div>
            <span class="badge badge-high">STEP 03</span>
          </div>
          <div class="indicator-detail">Review the explicit risk rating, linguistic flags, and safety advice.</div>
        </div>
        """, unsafe_allow_html=True)


# --- FULL WIDTH LOWER SECTION (RESULTS & ANALYTICS) ---
if message:
    pred, confidence, probs = predict_sms(model, message)
    if two_class:
        st.caption(f"Pitch-mode mapping: model predicted **{pred}** → user-facing class **{'scam' if pred == 'smishing' else 'safe/non-scam'}**")

    st.write("")
    res_col, why_col = st.columns([1.05, 0.95], gap="large")
    with res_col:
        render_result(pred, confidence)
        if probs:
            with st.container(border=True):
                st.markdown('<div class="section-title">Class probabilities</div>', unsafe_allow_html=True)
                prob_df = pd.DataFrame({"class": list(probs.keys()), "probability": list(probs.values())}).sort_values("probability", ascending=False)
                st.bar_chart(prob_df.set_index("class"), height=230)
    with why_col:
        with st.container(border=True):
            st.markdown('<div class="section-title">Why this was flagged</div>', unsafe_allow_html=True)
            for indicator in explain_message(message):
                render_indicator(indicator)

    with st.expander("Technical structural features detected"):
        feat = structural_features(message)
        st.dataframe(pd.DataFrame([feat]).T.rename(columns={0: "value"}), use_container_width=True)

st.write("")
st.markdown('<div class="section-title">Latest training analytics</div>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["Dataset", "Signals", "Model evaluation"])
# ... keep the rest of your tab rendering code exactly the same
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
