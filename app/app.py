from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


# --------------------------------------------------
# PAGE CONFIGURATION & FLUID STYLING
# --------------------------------------------------

st.set_page_config(
    page_title="Cybercrime Cash-Withdrawal Forecast",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def render_html(html_str: str):
    """
    Renders clean HTML without letting Markdown interpret 4+ space indentations as code blocks.
    """
    clean = "".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(clean, unsafe_allow_html=True)


# Fluid CSS & Professional Glassmorphic Theme
st.markdown("""
<style>
    /* ==============================================
       FLUID AMBIENT BACKGROUND & MESH GLOW
       ============================================== */
    @keyframes floatOrb1 {
        0% { transform: translate(0px, 0px) scale(1); }
        50% { transform: translate(35px, -45px) scale(1.15); }
        100% { transform: translate(-25px, 35px) scale(0.92); }
    }
    @keyframes floatOrb2 {
        0% { transform: translate(0px, 0px) scale(1); }
        50% { transform: translate(-40px, 35px) scale(1.12); }
        100% { transform: translate(30px, -30px) scale(0.95); }
    }
    @keyframes fluidSheen {
        0% { left: -100%; }
        50%, 100% { left: 100%; }
    }
    @keyframes pulseGlow {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.45; transform: scale(1.2); }
    }
    @keyframes waveMove {
        0% { transform: translate3d(-90px, 0, 0); }
        100% { transform: translate3d(85px, 0, 0); }
    }
    @keyframes liquidFillPulse {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.25) drop-shadow(0 0 10px rgba(59, 130, 246, 0.4)); }
    }

    /* Streamlit base container polish */
    .stApp {
        background-color: #0b0f19;
        background-image: 
            radial-gradient(circle at 15% 10%, rgba(37, 99, 235, 0.08) 0%, transparent 45%),
            radial-gradient(circle at 85% 85%, rgba(139, 92, 246, 0.07) 0%, transparent 45%),
            radial-gradient(circle at 50% 50%, rgba(14, 165, 233, 0.04) 0%, transparent 60%);
        background-attachment: fixed;
    }

    /* ==============================================
       METRIC CARDS WITH FLUID SHEEN & HOVER
       ============================================== */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(26, 34, 52, 0.75) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #38bdf8, transparent);
        animation: fluidSheen 4.5s linear infinite;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px) scale(1.01) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 12px 28px rgba(14, 165, 233, 0.2) !important;
    }

    /* ==============================================
       BUTTONS WITH FLUID GRADIENT & SHADOW
       ============================================== */
    .stButton > button {
        border-radius: 9px !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        color: #f1f5f9 !important;
        transition: all 0.25s ease-in-out !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 6px 18px rgba(56, 189, 248, 0.25) !important;
        color: #ffffff !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        border: 1px solid #60a5fa !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5) !important;
    }

    /* ==============================================
       PROFESSIONAL EXECUTIVE SIDEBAR STYLING
       ============================================== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #090d16 0%, #0d1322 50%, #111827 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4) !important;
    }
    section[data-testid="stSidebar"] div.stRadio > div {
        gap: 8px !important;
    }
    section[data-testid="stSidebar"] div.stRadio label {
        background: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
        padding: 9px 14px !important;
        transition: all 0.2s ease !important;
        margin-bottom: 2px !important;
        cursor: pointer !important;
    }
    section[data-testid="stSidebar"] div.stRadio label:hover {
        background: rgba(59, 130, 246, 0.15) !important;
        border-color: rgba(59, 130, 246, 0.35) !important;
        transform: translateX(3px) !important;
    }

    /* Sidebar info widgets */
    .sidebar-widget {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        padding: 12px 14px;
        margin-top: 10px;
        backdrop-filter: blur(8px);
    }

    /* Fluid live status indicator */
    .live-pulse {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #22c55e;
        margin-right: 6px;
        animation: pulseGlow 1.8s infinite;
        vertical-align: middle;
    }

    /* Parallax fluid wave header SVG */
    .fluid-waves {
        position: relative;
        width: 100%;
        height: 48px;
        margin-top: -8px;
        margin-bottom: -10px;
    }
    .parallax > use {
        animation: waveMove 25s cubic-bezier(.55,.5,.45,.5) infinite;
    }
    .parallax > use:nth-child(1) {
        animation-delay: -2s;
        animation-duration: 7s;
    }
    .parallax > use:nth-child(2) {
        animation-delay: -3s;
        animation-duration: 10s;
    }
    .parallax > use:nth-child(3) {
        animation-delay: -4s;
        animation-duration: 13s;
    }
    .parallax > use:nth-child(4) {
        animation-delay: -5s;
        animation-duration: 20s;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# PROJECT PATHS & ASSETS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "best_risk_classifier.joblib"
DATA_PATH = ROOT / "data" / "raw" / "synthetic_atm_data.csv"
RESULTS_PATH = ROOT / "results" / "phase4_test_metrics.csv"
CONFUSION_PATH = ROOT / "results" / "phase4_best_model_confusion_matrix.csv"
BATCH_SAMPLE_PATH = ROOT / "data" / "processed" / "batch_prediction_sample.csv"
SHAP_PATH = ROOT / "results" / "shap_high_risk_importance.png"
LIME_PATH = ROOT / "results" / "lime_high_risk_explanation.png"


# --------------------------------------------------
# LOAD MODEL & DATA (CACHED)
# --------------------------------------------------

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH, parse_dates=["date"])
    data = data.sort_values(["date", "zone_id"]).reset_index(drop=True)

    # Feature engineering
    data["withdrawals_per_atm"] = (
        data["withdrawal_count"] / data["atm_count"].replace(0, np.nan)
    )
    data["unusual_activity_ratio"] = (
        data["unusual_activity_count"] / data["withdrawal_count"].replace(0, np.nan)
    )
    data["avg_daily_incidents_30d"] = data["incidents_sum_30d"] / 30.0
    data["withdrawal_amount_per_atm"] = (
        data["total_withdrawal_amount"] / data["atm_count"].replace(0, np.nan)
    )

    day_index = (data["date"] - pd.Timestamp("2025-01-01")).dt.days
    data["season_30d_sin"] = np.sin(2 * np.pi * day_index / 30.0)
    data["season_30d_cos"] = np.cos(2 * np.pi * day_index / 30.0)

    data = data.replace([np.inf, -np.inf], np.nan)
    return data


try:
    bundle = load_model()
    df = load_data()

    model = bundle["model"]
    FEATURES = bundle["features"]
    TARGET = bundle["target"]
    CLASS_ORDER = bundle.get("class_order", ["Low", "Medium", "High"])
except Exception as error:
    st.error(f"Unable to load project files: {error}")
    st.stop()


# --------------------------------------------------
# COMPUTE ZONE LATEST STATUS FOR TELEMETRY
# --------------------------------------------------

zone_latest = (
    df.sort_values("date")
    .groupby("zone_id")
    .tail(1)
    .copy()
)
zone_latest["predicted_risk"] = model.predict(zone_latest[FEATURES])
zone_probabilities = model.predict_proba(zone_latest[FEATURES])
high_idx = list(model.classes_).index("High")
zone_latest["high_risk_probability"] = zone_probabilities[:, high_idx] * 100.0
zone_latest["confidence"] = zone_probabilities.max(axis=1) * 100.0

total_zones = len(zone_latest)
high_count = int((zone_latest["predicted_risk"] == "High").sum())
med_count = int((zone_latest["predicted_risk"] == "Medium").sum())
low_count = int((zone_latest["predicted_risk"] == "Low").sum())
avg_conf = float(zone_latest["confidence"].mean())
national_threat_index = float((high_count / total_zones) * 100.0)


# --------------------------------------------------
# ENHANCED PROFESSIONAL SIDEBAR
# --------------------------------------------------

with st.sidebar:
    # Sleek Executive Brand Header
    render_html("""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%);
                border: 1px solid rgba(56, 189, 248, 0.25);
                border-radius: 12px;
                padding: 16px 14px;
                margin-bottom: 15px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.3);">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="background: linear-gradient(135deg,#2563eb,#38bdf8);
                        width:38px;height:38px;border-radius:9px;
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.3rem;box-shadow:0 2px 10px rgba(37,99,235,0.4);">
                🛡️
            </div>
            <div>
                <div style="font-size:1.05rem;font-weight:700;color:#ffffff;letter-spacing:0.5px;">
                    CYBERSHIELD<span style="color:#38bdf8;">·AI</span>
                </div>
                <div style="font-size:0.75rem;color:#94a3b8;font-weight:500;">
                    ATM CASH-OUT FORECAST
                </div>
            </div>
        </div>
        <div style="margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.08);display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:0.75rem;color:#cbd5e1;">
                <span class="live-pulse"></span><strong>ENGINE ACTIVE</strong>
            </span>
            <span style="font-size:0.7rem;background:rgba(56,189,248,0.15);color:#38bdf8;padding:2px 8px;border-radius:12px;border:1px solid rgba(56,189,248,0.3);">
                v2.5 PRO
            </span>
        </div>
    </div>
    """)

    # Navigation Menu
    st.markdown("<p style='font-size:0.75rem;font-weight:700;letter-spacing:1px;color:#64748b;margin:0 0 6px 4px;'>SYSTEM MODULES</p>", unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard Overview",
            "🔍 Single Zone Risk Prediction",
            "📁 Batch CSV Prediction",
            "ℹ️ Model Intelligence & Explainability"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Fluid Liquid Threat Level Gauge Widget
    st.markdown("<p style='font-size:0.75rem;font-weight:700;letter-spacing:1px;color:#64748b;margin:0 0 6px 4px;'>NATIONAL THREAT INDEX</p>", unsafe_allow_html=True)
    render_html(f"""
    <div class="sidebar-widget" style="border-left: 3px solid #ef4444;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:0.8rem;color:#94a3b8;font-weight:600;">ELEVATED SYNDICATE RISK</span>
            <span style="font-size:0.85rem;color:#ef4444;font-weight:700;">{national_threat_index:.1f}%</span>
        </div>
        <div style="width:100%;height:8px;background:#1e293b;border-radius:6px;overflow:hidden;margin:8px 0;display:flex;">
            <div style="width:{high_count/total_zones*100}%;background:#ef4444;transition:all 0.5s ease;"></div>
            <div style="width:{med_count/total_zones*100}%;background:#f59e0b;transition:all 0.5s ease;"></div>
            <div style="width:{low_count/total_zones*100}%;background:#22c55e;transition:all 0.5s ease;"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#cbd5e1;padding-top:2px;">
            <span><strong style="color:#ef4444;">{high_count}</strong> High</span>
            <span><strong style="color:#f59e0b;">{med_count}</strong> Med</span>
            <span><strong style="color:#22c55e;">{low_count}</strong> Low</span>
        </div>
    </div>
    """)

    # Interactive Zone Quick-Inspector in Sidebar
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.75rem;font-weight:700;letter-spacing:1px;color:#64748b;margin:0 0 6px 4px;'>QUICK ZONE TELEMETRY</p>", unsafe_allow_html=True)
    selected_quick_zone = st.selectbox(
        "Select Zone to Inspect",
        sorted(zone_latest["zone_id"].unique().tolist()),
        index=0,
        label_visibility="collapsed"
    )
    qz_info = zone_latest[zone_latest["zone_id"] == selected_quick_zone].iloc[0]
    qz_color = "#ef4444" if qz_info["predicted_risk"] == "High" else ("#f59e0b" if qz_info["predicted_risk"] == "Medium" else "#22c55e")
    
    render_html(f"""
    <div class="sidebar-widget" style="border-top: 2px solid {qz_color};">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <strong style="color:#ffffff;font-size:0.9rem;">{qz_info['city']}</strong>
            <span style="font-size:0.75rem;background:{qz_color}25;color:{qz_color};border:1px solid {qz_color};padding:2px 8px;border-radius:6px;font-weight:700;">
                {qz_info['predicted_risk']} Risk
            </span>
        </div>
        <div style="font-size:0.75rem;color:#94a3b8;margin-top:4px;">
            {qz_info['state']} · {int(qz_info['atm_count'])} ATMs
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:8px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.06);font-size:0.75rem;">
            <span style="color:#cbd5e1;">High Risk Probability:</span>
            <span style="color:{qz_color};font-weight:700;">{qz_info['high_risk_probability']:.1f}%</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:0.75rem;margin-top:2px;">
            <span style="color:#cbd5e1;">24h Withdrawals:</span>
            <span style="color:#ffffff;font-weight:600;">{int(qz_info['withdrawal_count'])}</span>
        </div>
    </div>
    """)

    # Model Hardware & Spec Card
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.75rem;font-weight:700;letter-spacing:1px;color:#64748b;margin:0 0 6px 4px;'>SYSTEM SPECIFICATIONS</p>", unsafe_allow_html=True)
    render_html("""
    <div class="sidebar-widget" style="font-size:0.75rem;color:#94a3b8;line-height:1.6;">
        <div>🧠 <strong>Classifier:</strong> Tuned Logistic Pipeline</div>
        <div>⏱️ <strong>Forecast Horizon:</strong> 7-Day Window</div>
        <div>📡 <strong>Input Features:</strong> 23 Synthesized Signals</div>
        <div>📍 <strong>Scope:</strong> 30 Zones across 10 States</div>
        <div style="margin-top:6px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.06);color:#64748b;">
            🔒 256-Bit Telemetry · Synthetic Demo
        </div>
    </div>
    """)


# --------------------------------------------------
# 1. DASHBOARD OVERVIEW (FLUID HERO & DYNAMIC MAP)
# --------------------------------------------------

if page == "📊 Dashboard Overview":

    # Fluid Hero Banner with Real-Time Parallax Waves
    render_html("""
    <div style="background: linear-gradient(135deg, #090d16 0%, #0f172a 40%, #1e3a8a 100%);
                border: 1px solid rgba(56, 189, 248, 0.25);
                border-radius: 16px;
                padding: 26px 30px 0px 30px;
                margin-bottom: 24px;
                position: relative;
                overflow: hidden;
                box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.4);">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;position:relative;z-index:2;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <span class="live-pulse"></span>
                    <span style="font-size:0.8rem;letter-spacing:1.5px;color:#38bdf8;font-weight:700;">
                        REAL-TIME GEOSPATIAL INTELLIGENCE
                    </span>
                </div>
                <h1 style="color:#ffffff;margin:0;font-size:2.1rem;font-weight:800;letter-spacing:-0.5px;">
                    Cybercrime Risk Intelligence Dashboard
                </h1>
                <p style="color:#94a3b8;margin:8px 0 16px 0;font-size:1.02rem;max-width:750px;">
                    AI-powered continuous forecasting of cashout incidents and coordinated ATM fraud syndicates across Indian metropolitan clusters.
                </p>
            </div>
            <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;position:relative;z-index:2;">
                <span style="background:rgba(56,189,248,0.15);color:#38bdf8;padding:6px 14px;border-radius:20px;font-size:0.8rem;font-weight:700;border:1px solid rgba(56,189,248,0.35);">
                    7-DAY LOOKAHEAD FORECAST
                </span>
                <span style="font-size:0.75rem;color:#64748b;">
                    Simulated Telemetry Stream
                </span>
            </div>
        </div>
        <svg class="fluid-waves" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 24 150 28" preserveAspectRatio="none" shape-rendering="auto">
            <defs>
                <path id="gentle-wave" d="M-160 44c30 0 58-18 88-18s 58 18 88 18 58-18 88-18 58 18 88 18 v44h-352z" />
            </defs>
            <g class="parallax">
                <use xlink:href="#gentle-wave" href="#gentle-wave" x="48" y="0" fill="rgba(37, 99, 235, 0.2)" />
                <use xlink:href="#gentle-wave" href="#gentle-wave" x="48" y="3" fill="rgba(56, 189, 248, 0.25)" />
                <use xlink:href="#gentle-wave" href="#gentle-wave" x="48" y="5" fill="rgba(99, 102, 241, 0.15)" />
                <use xlink:href="#gentle-wave" href="#gentle-wave" x="48" y="7" fill="rgba(11, 15, 25, 0.85)" />
            </g>
        </svg>
    </div>
    """)

    # Top KPI Metrics Cards with Fluid Glow
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total ATM Zones", total_zones, "10 Indian States Covered")
    k2.metric("🔴 High Risk Hubs", f"{high_count}", f"{(high_count/total_zones)*100:.1f}% National Ratio", delta_color="inverse")
    k3.metric("🟠 Medium Risk Hubs", f"{med_count}", f"{(med_count/total_zones)*100:.1f}% Surveillance", delta_color="off")
    k4.metric("🟢 Low Risk Hubs", f"{low_count}", f"{(low_count/total_zones)*100:.1f}% Nominal Baseline", delta_color="normal")
    k5.metric("🎯 Mean Confidence", f"{avg_conf:.1f}%", "Classifier Certainty")

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------
    # GEOGRAPHIC RISK INTELLIGENCE & INDIA ATM MAP
    # --------------------------------------------------
    st.markdown("### 🇮🇳 Geographic Risk Intelligence & India ATM Map")
    st.caption("Interactive geospatial view of all 30 simulated ATM zones with live risk classifications and telemetry.")

    # State Session Management
    if "filter_risk" not in st.session_state:
        st.session_state["filter_risk"] = "All Risks"
    if "filter_state" not in st.session_state:
        st.session_state["filter_state"] = "All States"
    if "filter_city" not in st.session_state:
        st.session_state["filter_city"] = "All Cities"

    # Action Filter Buttons
    btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns([1.2, 1.3, 1.3, 1.2, 1.2])
    with btn_col1:
        if st.button("🌐 All Zones (30)", use_container_width=True):
            st.session_state["filter_risk"] = "All Risks"
            st.session_state["filter_state"] = "All States"
            st.session_state["filter_city"] = "All Cities"
    with btn_col2:
        if st.button("🔴 High Risk (6)", use_container_width=True):
            st.session_state["filter_risk"] = "High"
    with btn_col3:
        if st.button("🟠 Medium Risk (19)", use_container_width=True):
            st.session_state["filter_risk"] = "Medium"
    with btn_col4:
        if st.button("🟢 Low Risk (5)", use_container_width=True):
            st.session_state["filter_risk"] = "Low"
    with btn_col5:
        if st.button("🔄 Reset Filters", use_container_width=True):
            st.session_state["filter_risk"] = "All Risks"
            st.session_state["filter_state"] = "All States"
            st.session_state["filter_city"] = "All Cities"

    # Dropdown Filters & Basemap Style
    f_c1, f_c2, f_c3, f_c4 = st.columns([1.2, 1.2, 1.1, 1.1])
    with f_c1:
        state_list = ["All States"] + sorted(zone_latest["state"].unique().tolist())
        selected_state = st.selectbox(
            "Filter by State",
            state_list,
            index=state_list.index(st.session_state["filter_state"])
            if st.session_state["filter_state"] in state_list else 0,
            key="sb_state"
        )
        if selected_state != st.session_state["filter_state"]:
            st.session_state["filter_state"] = selected_state
            st.session_state["filter_city"] = "All Cities"

    with f_c2:
        if st.session_state["filter_state"] != "All States":
            available_cities = ["All Cities"] + sorted(
                zone_latest[zone_latest["state"] == st.session_state["filter_state"]]["city"].unique().tolist()
            )
        else:
            available_cities = ["All Cities"] + sorted(zone_latest["city"].unique().tolist())

        city_idx = (
            available_cities.index(st.session_state["filter_city"])
            if st.session_state["filter_city"] in available_cities else 0
        )
        selected_city = st.selectbox(
            "Filter by City",
            available_cities,
            index=city_idx,
            key="sb_city"
        )
        st.session_state["filter_city"] = selected_city

    with f_c3:
        risk_options = ["All Risks", "High", "Medium", "Low"]
        selected_risk = st.selectbox(
            "Filter by Risk Level",
            risk_options,
            index=risk_options.index(st.session_state["filter_risk"])
            if st.session_state["filter_risk"] in risk_options else 0,
            key="sb_risk"
        )
        st.session_state["filter_risk"] = selected_risk

    with f_c4:
        map_style = st.selectbox(
            "Map Basemap Style",
            ["open-street-map", "carto-darkmatter", "carto-positron"],
            index=0,
            key="sb_style"
        )

    # Filtered dataset
    filtered_map = zone_latest.copy()
    if st.session_state["filter_state"] != "All States":
        filtered_map = filtered_map[filtered_map["state"] == st.session_state["filter_state"]]
    if st.session_state["filter_city"] != "All Cities":
        filtered_map = filtered_map[filtered_map["city"] == st.session_state["filter_city"]]
    if st.session_state["filter_risk"] != "All Risks":
        filtered_map = filtered_map[filtered_map["predicted_risk"] == st.session_state["filter_risk"]]

    # Auto Center & Zoom Calculation
    if st.session_state["filter_city"] != "All Cities" and not filtered_map.empty:
        map_center = {
            "lat": float(filtered_map["latitude"].mean()),
            "lon": float(filtered_map["longitude"].mean())
        }
        map_zoom = 9.5
    elif st.session_state["filter_state"] != "All States" and not filtered_map.empty:
        map_center = {
            "lat": float(filtered_map["latitude"].mean()),
            "lon": float(filtered_map["longitude"].mean())
        }
        map_zoom = 6.2
    else:
        # Perfectly frames all 30 points across India (Punjab to Tamil Nadu, Gujarat to WB)
        map_center = {"lat": 22.0, "lon": 79.0}
        map_zoom = 3.8

    risk_colors = {
        "High": "#ef4444",
        "Medium": "#f59e0b",
        "Low": "#22c55e"
    }

    # Side-by-Side Map and Analytics
    map_col, stats_col = st.columns([1.8, 1.0])

    with map_col:
        if filtered_map.empty:
            st.warning(f"No ATM zones match the active filter: State='{st.session_state['filter_state']}', City='{st.session_state['filter_city']}', Risk='{st.session_state['filter_risk']}'.")
        else:
            st.caption(f"📍 Displaying **{len(filtered_map)}** of **{len(zone_latest)}** ATM zones across India.")

            fig_map = px.scatter_map(
                filtered_map,
                lat="latitude",
                lon="longitude",
                color="predicted_risk",
                color_discrete_map=risk_colors,
                hover_name="city",
                hover_data={
                    "zone_id": True,
                    "state": True,
                    "predicted_risk": True,
                    "confidence": ":.1f",
                    "atm_count": True,
                    "withdrawal_count": True,
                    "latitude": False,
                    "longitude": False
                },
                zoom=map_zoom,
                center=map_center,
                height=560,
                map_style=map_style,
                title=f"India ATM Zones ({len(filtered_map)} Plotted)"
            )

            # Prominent markers with border & high opacity
            fig_map.update_traces(
                marker=dict(size=14, opacity=0.92)
            )

            fig_map.update_layout(
                margin=dict(l=0, r=0, t=40, b=0),
                legend_title_text="Predicted Risk",
                legend=dict(
                    yanchor="top",
                    y=0.98,
                    xanchor="left",
                    x=0.02,
                    bgcolor="rgba(15,23,42,0.85)"
                )
            )

            st.plotly_chart(fig_map, use_container_width=True)

    with stats_col:
        st.markdown("#### 📊 Risk Distribution")

        risk_dist = (
            zone_latest["predicted_risk"]
            .value_counts()
            .reindex(["High", "Medium", "Low"])
            .fillna(0)
            .reset_index()
        )
        risk_dist.columns = ["Risk Level", "Zones"]

        donut = px.pie(
            risk_dist,
            names="Risk Level",
            values="Zones",
            hole=0.62,
            color="Risk Level",
            color_discrete_map=risk_colors
        )
        donut.update_layout(
            height=260,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
        )
        st.plotly_chart(donut, use_container_width=True)

        st.markdown("#### 🚨 Top High-Risk Watchlist")
        top_high = zone_latest.sort_values("high_risk_probability", ascending=False).head(4)
        for _, row in top_high.iterrows():
            render_html(f"""
            <div style="background: rgba(30, 41, 59, 0.7);
                        padding: 9px 12px;
                        border-radius: 8px;
                        margin-bottom: 7px;
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                        border: 1px solid rgba(255,255,255,0.05);
                        border-left: 4px solid #ef4444;">
                <div>
                    <strong>{row['city']}</strong> <span style="color:#94a3b8;font-size:0.85rem;">({row['zone_id']})</span><br>
                    <span style="font-size:0.8rem;color:#cbd5e1;">{row['state']} · {int(row['atm_count'])} ATMs</span>
                </div>
                <div style="text-align:right;">
                    <span style="color:#ef4444;font-weight:700;font-size:0.95rem;">{row['high_risk_probability']:.1f}%</span><br>
                    <span style="font-size:0.75rem;color:#94a3b8;">High Risk Prob</span>
                </div>
            </div>
            """)

    st.divider()

    # --------------------------------------------------
    # STATE-WISE RISK ANALYTICS & REGIONAL BREAKDOWN
    # --------------------------------------------------
    st.markdown("### 📊 State-Wise Risk Analytics & Regional Hotspots")
    st.caption("Cross-state comparison of predicted risk categories and syndicate threat vulnerability across 10 Indian states.")

    sw_c1, sw_c2 = st.columns([1.6, 1.2])

    with sw_c1:
        # Stacked bar chart of zones by risk category per state
        state_risk_df = (
            zone_latest.groupby(["state", "predicted_risk"])
            .size()
            .reset_index(name="Zone Count")
        )

        high_counts = (
            zone_latest[zone_latest["predicted_risk"] == "High"]
            .groupby("state")
            .size()
            .to_dict()
        )
        state_order = sorted(
            zone_latest["state"].unique(),
            key=lambda s: (high_counts.get(s, 0), zone_latest[zone_latest["state"] == s]["high_risk_probability"].mean()),
            reverse=True
        )

        fig_state_bar = px.bar(
            state_risk_df,
            x="state",
            y="Zone Count",
            color="predicted_risk",
            category_orders={"state": state_order, "predicted_risk": ["High", "Medium", "Low"]},
            color_discrete_map=risk_colors,
            title="Simulated ATM Zone Risk Distribution by State",
            barmode="stack",
            height=340
        )
        fig_state_bar.update_layout(
            margin=dict(l=10, r=10, t=40, b=20),
            xaxis_title="",
            yaxis_title="ATM Zones",
            legend_title_text="Risk Level",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_state_bar, use_container_width=True)

    with sw_c2:
        # State vulnerability ranking (Average High Risk Probability)
        state_ranking = (
            zone_latest.groupby("state")
            .agg(
                avg_high_risk=("high_risk_probability", "mean"),
                total_atms=("atm_count", "sum"),
                high_zones=("predicted_risk", lambda s: (s == "High").sum())
            )
            .reset_index()
            .sort_values("avg_high_risk", ascending=False)
        )

        fig_vuln = px.bar(
            state_ranking,
            x="avg_high_risk",
            y="state",
            orientation="h",
            text=state_ranking["avg_high_risk"].apply(lambda v: f"{v:.1f}%"),
            title="State Vulnerability Index (Mean High-Risk Prob %)",
            color="avg_high_risk",
            color_continuous_scale="Reds",
            height=340
        )
        fig_vuln.update_layout(
            margin=dict(l=10, r=10, t=40, b=20),
            xaxis_title="Average High Risk Probability (%)",
            yaxis_title="",
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_vuln, use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # HISTORICAL ANALYTICS & ZONE DRILL-DOWN INSPECTOR
    # --------------------------------------------------
    st.markdown("### 📈 Historical Zone Trends & Drill-Down Inspector")
    st.caption(
        "Inspect a specific zone's historical simulated activity alongside its future 7-day model forecast. "
        "Note: Historical simulated outcomes (past observations) are distinct from future model probability forecasts."
    )

    avail_zones = sorted(filtered_map["zone_id"].unique().tolist()) if len(filtered_map) > 0 else sorted(zone_latest["zone_id"].unique().tolist())
    zone_label_map = {
        row["zone_id"]: f"{row['zone_id']} — {row['city']}, {row['state']} ({row['predicted_risk']} Forecast)"
        for _, row in zone_latest.iterrows()
    }

    hz_c1, hz_c2 = st.columns([2.2, 1.8])
    with hz_c1:
        drill_zone = st.selectbox(
            "Select Zone for Historical Drill-Down",
            avail_zones,
            format_func=lambda z: zone_label_map.get(z, z),
            key="overview_drill_zone"
        )
    with hz_c2:
        lookback_choice = st.radio(
            "Historical Time Window",
            ["Last 30 Days", "Last 90 Days", "Full Historical Span"],
            index=1,
            horizontal=True,
            key="overview_lookback"
        )

    z_hist = df[df["zone_id"] == drill_zone].sort_values("date").copy()
    if lookback_choice == "Last 30 Days":
        z_hist = z_hist.tail(30)
    elif lookback_choice == "Last 90 Days":
        z_hist = z_hist.tail(90)

    z_curr = zone_latest[zone_latest["zone_id"] == drill_zone].iloc[0]
    z_badge_col = "#ef4444" if z_curr["predicted_risk"] == "High" else ("#f59e0b" if z_curr["predicted_risk"] == "Medium" else "#22c55e")

    # Side-by-side cards: Past Simulated Outcomes vs Future 7-Day Model Forecast
    dc_1, dc_2 = st.columns(2)
    with dc_1:
        render_html(f"""
        <div style="background:rgba(15, 23, 42, 0.85);border:1px solid rgba(56, 189, 248, 0.35);border-radius:12px;padding:16px 20px;">
            <div style="font-size:0.76rem;font-weight:700;color:#38bdf8;letter-spacing:1px;margin-bottom:6px;">
                📊 HISTORICAL SIMULATED CONTEXT (OBSERVED ≤ {latest_date.strftime('%Y-%m-%d')})
            </div>
            <div style="font-size:1.1rem;font-weight:700;color:#ffffff;margin-bottom:8px;">
                {z_curr['city']}, {z_curr['state']} ({z_curr['zone_id']}) · {int(z_curr['atm_count'])} Simulated ATMs
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.84rem;color:#cbd5e1;">
                <div>• <strong>Latest 24h Withdrawals:</strong> {int(z_curr['withdrawal_count'])} txns</div>
                <div>• <strong>Latest 24h Unusual Signals:</strong> {int(z_curr['unusual_activity_count'])}</div>
                <div>• <strong>Past 7d Incident Sum:</strong> {int(z_curr['incidents_sum_7d'])} simulated</div>
                <div>• <strong>Past 30d Incident Sum:</strong> {int(z_curr['incidents_sum_30d'])} simulated</div>
            </div>
        </div>
        """)
    with dc_2:
        render_html(f"""
        <div style="background:rgba(15, 23, 42, 0.85);border:1px solid {z_badge_col};border-radius:12px;padding:16px 20px;">
            <div style="font-size:0.76rem;font-weight:700;color:{z_badge_col};letter-spacing:1px;margin-bottom:6px;">
                🔮 FUTURE 7-DAY MODEL FORECAST (ESTIMATED t+1 TO t+7)
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="font-size:1.1rem;font-weight:800;color:#ffffff;">Predicted Class: <span style="color:{z_badge_col};">{z_curr['predicted_risk'].upper()} RISK</span></span>
                <span style="background:{z_badge_col}25;color:{z_badge_col};border:1px solid {z_badge_col};padding:2px 10px;border-radius:12px;font-size:0.78rem;font-weight:700;">
                    {z_curr['confidence']:.1f}% Confidence
                </span>
            </div>
            <div style="font-size:0.83rem;color:#cbd5e1;line-height:1.5;">
                • <strong>Estimated High-Risk Probability:</strong> {z_curr['high_risk_probability']:.1f}% (Model Estimate)<br>
                • <em>Disclaimer: Forecast probabilities represent statistical model estimates on synthetic data, not confirmed real-world crime incidents.</em>
            </div>
        </div>
        """)

    tr_c1, tr_c2 = st.columns(2)
    with tr_c1:
        fig_z_trend = go.Figure()
        fig_z_trend.add_trace(go.Scatter(
            x=z_hist["date"], y=z_hist["withdrawal_count"],
            mode="lines", name="Daily Withdrawals",
            line=dict(color="#38bdf8", width=2)
        ))
        fig_z_trend.add_trace(go.Scatter(
            x=z_hist["date"], y=z_hist["unusual_activity_sum_7d"],
            mode="lines", name="7d Unusual Activity Sum",
            line=dict(color="#f59e0b", width=2, dash="dot"),
            yaxis="y2"
        ))
        fig_z_trend.update_layout(
            title=f"Historical Withdrawals & 7d Unusual Signals ({drill_zone})",
            height=320,
            margin=dict(l=10, r=10, t=40, b=20),
            xaxis_title="Observation Date",
            yaxis=dict(title="Daily Withdrawals"),
            yaxis2=dict(title="7d Unusual Signals", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_z_trend, use_container_width=True)

    with tr_c2:
        fig_inc_trend = go.Figure()
        fig_inc_trend.add_trace(go.Bar(
            x=z_hist["date"], y=z_hist["cashout_incident_count"],
            name="Simulated Daily Incidents (Observed)",
            marker_color="#ef4444", opacity=0.75
        ))
        fig_inc_trend.add_trace(go.Scatter(
            x=z_hist["date"], y=z_hist["incidents_sum_7d"],
            mode="lines", name="Lagging 7d Incident Total",
            line=dict(color="#a855f7", width=2.2)
        ))
        fig_inc_trend.update_layout(
            title=f"Historical Simulated Incident Outcomes ({drill_zone})",
            height=320,
            margin=dict(l=10, r=10, t=40, b=20),
            xaxis_title="Observation Date",
            yaxis_title="Simulated Incident Count",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_inc_trend, use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # ZONE-WISE DETAILED RANKING TABLE & EXPORT
    # --------------------------------------------------
    st.markdown("### 📋 Zone-Wise Forecast Rankings")

    tbl_c1, tbl_c2 = st.columns([3, 1])
    with tbl_c1:
        st.caption("Complete tabular ranking sorted by risk probability. Search or filter below.")
    with tbl_c2:
        csv_data = filtered_map[[
            "zone_id", "city", "state", "predicted_risk", "confidence",
            "high_risk_probability", "atm_count", "withdrawal_count"
        ]].to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Export Visible Zones (CSV)",
            data=csv_data,
            file_name="cybercrime_risk_zones.csv",
            mime="text/csv",
            use_container_width=True
        )

    ranking_df = filtered_map[[
        "zone_id", "city", "state", "predicted_risk",
        "confidence", "high_risk_probability", "atm_count", "withdrawal_count"
    ]].sort_values("high_risk_probability", ascending=False)

    ranking_df.columns = [
        "Zone ID", "City", "State", "Predicted Risk",
        "Confidence (%)", "High Risk Prob (%)", "ATM Count", "24h Withdrawals"
    ]

    st.dataframe(
        ranking_df.style.format({
            "Confidence (%)": "{:.1f}%",
            "High Risk Prob (%)": "{:.1f}%",
            "ATM Count": "{:.0f}",
            "24h Withdrawals": "{:.0f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    with st.expander("🔍 View Raw Historical Time-Series Dataset (First 20 Records)"):
        st.dataframe(df.head(20), use_container_width=True)


# --------------------------------------------------
# 2. SINGLE ZONE RISK PREDICTION
# --------------------------------------------------

elif page == "🔍 Single Zone Risk Prediction":

    render_html("""
    <div style="background: linear-gradient(135deg, #090d16 0%, #064e3b 100%);
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 14px;
                padding: 24px 28px;
                margin-bottom: 22px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);">
        <h1 style="color:white;margin:0;font-size:1.9rem;font-weight:700;">
            Individual Zone Risk Inference
        </h1>
        <p style="color:#a7f3d0;margin:6px 0 0 0;font-size:1rem;">
            Simulate or fine-tune specific zone activity metrics to predict 7-day cybercrime cashout probability.
        </p>
    </div>
    """)

    # --------------------------------------------------
    # SYNDICATE CASHOUT ATTACK INJECTION SIMULATOR
    # --------------------------------------------------
    render_html("""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.9) 100%);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 12px;
                padding: 16px 20px;
                margin-bottom: 16px;">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:1.4rem;">⚡</span>
                <div>
                    <strong style="color:#ffffff;font-size:1.05rem;">Adversarial Syndicate Cashout Simulation Engine</strong>
                    <div style="font-size:0.82rem;color:#94a3b8;margin-top:2px;">
                        Test real-time classifier sensitivity by injecting sudden cashout surges and rapid card retry anomalies.
                    </div>
                </div>
            </div>
        </div>
    </div>
    """)

    sim_col1, sim_col2 = st.columns([2.8, 1.2])
    with sim_col1:
        attack_injected = st.toggle(
            "⚡ Inject Simulated Syndicate Cashout Attack",
            value=st.session_state.get("attack_active", False),
            key="syndicate_attack_toggle",
            help="Simulates an immediate coordinated syndicate attack: 15 consecutive card re-tries and ₹6,00,000 withdrawal surge"
        )
        st.session_state["attack_active"] = attack_injected

    with sim_col2:
        if attack_injected:
            render_html("""
            <div style="background:rgba(239, 68, 68, 0.2);border:1px solid #ef4444;border-radius:8px;padding:8px 14px;display:flex;align-items:center;gap:8px;">
                <span class="live-pulse" style="background:#ef4444;"></span>
                <span style="color:#f87171;font-size:0.82rem;font-weight:800;letter-spacing:0.5px;">ATTACK ACTIVE (SURGE INJECTED)</span>
            </div>
            """)
        else:
            render_html("""
            <div style="background:rgba(34, 197, 94, 0.12);border:1px solid rgba(34, 197, 94, 0.3);border-radius:8px;padding:8px 14px;display:flex;align-items:center;gap:8px;">
                <span class="live-pulse" style="background:#22c55e;"></span>
                <span style="color:#22c55e;font-size:0.82rem;font-weight:600;">System Standby · Nominal</span>
            </div>
            """)

    attack_preset = {
        "zone_id": "ZONE_017", "state": "Maharashtra", "city": "Pune", "atm_count": 12.0,
        "withdrawal_count": 180.0, "avg_withdrawal_amount": 3893.3, "total_withdrawal_amount": 700800.0,
        "unusual_activity_count": 15.0, "withdrawals_sum_7d": 910.0, "unusual_activity_sum_7d": 48.0,
        "incidents_sum_7d": 4.0, "withdrawals_sum_30d": 2000.0, "unusual_activity_sum_30d": 57.0,
        "incidents_sum_30d": 5.0, "month": 3, "day_of_week": 2, "is_weekend": 0
    }

    if attack_injected:
        # Emergency Notification Banner & Audio Siren
        st.toast(
            "🚨 CRITICAL ALERT: Syndicate Cashout Attack Injected! Unusual activity spiked (+15) and ₹6,00,000 cash surge detected!",
            icon="🚨"
        )

        # Audio Siren (Dual Delivery: Base64 WAV audio tag + Web Audio API synthesizer fallback)
        try:
            b64_sound_path = Path(__file__).resolve().parent / "alert_sound.b64"
            if b64_sound_path.exists():
                b64_audio = b64_sound_path.read_text().strip()
                audio_component = f"""
                <audio id="alert-siren" autoplay>
                    <source src="data:audio/wav;base64,{b64_audio}" type="audio/wav">
                </audio>
                <script>
                    const audio = document.getElementById('alert-siren');
                    if (audio) {{
                        audio.volume = 0.7;
                        audio.play().catch(function(err) {{
                            try {{
                                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                                const osc = ctx.createOscillator();
                                const gain = ctx.createGain();
                                osc.type = 'sawtooth';
                                osc.frequency.setValueAtTime(850, ctx.currentTime);
                                osc.frequency.linearRampToValueAtTime(450, ctx.currentTime + 0.35);
                                gain.gain.setValueAtTime(0.25, ctx.currentTime);
                                gain.gain.linearRampToValueAtTime(0.01, ctx.currentTime + 0.4);
                                osc.connect(gain);
                                gain.connect(ctx.destination);
                                osc.start();
                                osc.stop(ctx.currentTime + 0.4);
                            }} catch(e) {{}}
                        }});
                    }}
                </script>
                """
                components.html(audio_component, height=0, width=0)
        except Exception:
            pass

        # Compute Model Inference in Real Time for Baseline vs Attack
        base_scenario = {
            "zone_id": "ZONE_017", "latitude": 18.5204, "longitude": 73.8567,
            "day_of_week": 2, "month": 3, "is_weekend": 0,
            "atm_count": 12.0, "withdrawal_count": 48.0, "avg_withdrawal_amount": 2100.0,
            "total_withdrawal_amount": 100800.0, "unusual_activity_count": 0.0,
            "withdrawals_sum_7d": 310.0, "unusual_activity_sum_7d": 3.0, "incidents_sum_7d": 0.0,
            "withdrawals_sum_30d": 1400.0, "unusual_activity_sum_30d": 12.0, "incidents_sum_30d": 1.0,
            "withdrawals_per_atm": 48.0 / 12.0, "unusual_activity_ratio": 0.0,
            "avg_daily_incidents_30d": 1.0 / 30.0, "withdrawal_amount_per_atm": 100800.0 / 12.0,
            "season_30d_sin": 0.0, "season_30d_cos": 1.0
        }
        df_base = pd.DataFrame([base_scenario])[FEATURES]
        pred_base_label = model.predict(df_base)[0]
        probs_base = model.predict_proba(df_base)[0]
        probs_base_map = dict(zip(model.classes_, probs_base))

        attack_scenario = base_scenario.copy()
        attack_scenario["withdrawal_count"] = 180.0
        attack_scenario["unusual_activity_count"] = 15.0
        attack_scenario["total_withdrawal_amount"] = 700800.0
        attack_scenario["avg_withdrawal_amount"] = 700800.0 / 180.0
        attack_scenario["withdrawals_sum_7d"] = 310.0 + 600.0
        attack_scenario["unusual_activity_sum_7d"] = 3.0 + 45.0
        attack_scenario["incidents_sum_7d"] = 4.0
        attack_scenario["withdrawals_per_atm"] = 180.0 / 12.0
        attack_scenario["unusual_activity_ratio"] = 15.0 / 180.0
        attack_scenario["withdrawal_amount_per_atm"] = 700800.0 / 12.0

        df_attack = pd.DataFrame([attack_scenario])[FEATURES]
        pred_attack_label = model.predict(df_attack)[0]
        probs_attack = model.predict_proba(df_attack)[0]
        probs_attack_map = dict(zip(model.classes_, probs_attack))

        # Real-Time Model Flip Visualizer Header
        render_html("""
        <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.22) 0%, rgba(15, 23, 42, 0.95) 100%);
                    border: 2px solid #ef4444;
                    border-radius: 14px;
                    padding: 20px 24px;
                    margin: 16px 0 20px 0;
                    box-shadow: 0 0 30px rgba(239, 68, 68, 0.3);">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
                <div style="display:flex;align-items:center;gap:14px;">
                    <span style="font-size:2rem;animation:pulseGlow 1.2s infinite;display:inline-block;">🚨</span>
                    <div>
                        <div style="font-size:1.15rem;font-weight:800;color:#fca5a5;letter-spacing:0.5px;">
                            CRITICAL THREAT INJECTION: SYNDICATE CASHOUT ACTIVE
                        </div>
                        <div style="font-size:0.86rem;color:#cbd5e1;margin-top:2px;">
                            Simulated Adversarial Surge: <strong>+15 Consecutive Card Re-tries</strong> &amp; <strong>+₹6,00,000 Cash Withdrawal Burst</strong> in Pune (ZONE_017)
                        </div>
                    </div>
                </div>
                <div style="background:#ef4444;color:white;padding:6px 16px;border-radius:20px;font-size:0.8rem;font-weight:800;letter-spacing:1px;box-shadow:0 0 12px rgba(239,68,68,0.5);">
                    ⚡ MODEL RISK FLIPPED: LOW ➔ HIGH
                </div>
            </div>
        </div>
        """)

        # 3 Side-by-Side Flip Comparison Cards
        flip_c1, flip_c2, flip_c3 = st.columns([1.3, 1, 1.3])

        with flip_c1:
            render_html(f"""
            <div style="background:rgba(15, 23, 42, 0.85);border:1px solid rgba(34, 197, 94, 0.45);border-radius:12px;padding:18px;height:100%;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                    <span style="font-size:0.78rem;font-weight:700;letter-spacing:1px;color:#94a3b8;">1. NORMAL BASELINE</span>
                    <span style="background:rgba(34,197,94,0.18);color:#22c55e;border:1px solid #22c55e;padding:3px 10px;border-radius:12px;font-size:0.75rem;font-weight:800;">
                        🟢 {pred_base_label.upper()} RISK
                    </span>
                </div>
                <div style="font-size:1.35rem;font-weight:800;color:#22c55e;margin-bottom:8px;">
                    {probs_base_map.get('Low', 0.0)*100:.1f}% Low Risk Confidence
                </div>
                <div style="font-size:0.82rem;color:#94a3b8;line-height:1.7;">
                    <div>• 24h Cashout: <strong style="color:#ffffff;">₹{int(base_scenario['total_withdrawal_amount']):,}</strong></div>
                    <div>• Unusual Signals: <strong style="color:#ffffff;">{int(base_scenario['unusual_activity_count'])}</strong> (0 card retries)</div>
                    <div>• High-Risk Prob: <span style="color:#94a3b8;">{probs_base_map.get('High', 0.0)*100:.1f}%</span></div>
                    <div>• System State: <span style="color:#22c55e;font-weight:600;">Nominal Routine Operations</span></div>
                </div>
            </div>
            """)

        with flip_c2:
            prob_high_delta = (probs_attack_map.get('High', 0.0) - probs_base_map.get('High', 0.0)) * 100
            prob_low_delta = (probs_attack_map.get('Low', 0.0) - probs_base_map.get('Low', 0.0)) * 100
            render_html(f"""
            <div style="background:linear-gradient(180deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.95) 100%);border:1px dashed #ef4444;border-radius:12px;padding:18px;height:100%;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;">
                <div style="font-size:0.75rem;font-weight:700;letter-spacing:1px;color:#f87171;margin-bottom:6px;">
                    REAL-TIME MODEL FLIP
                </div>
                <div style="font-size:1.7rem;font-weight:900;color:#ef4444;margin:4px 0;">
                    🟢 ➔ 🔴
                </div>
                <div style="font-size:0.9rem;font-weight:800;color:#ffffff;margin-bottom:8px;">
                    LOW ➔ HIGH RISK
                </div>
                <div style="background:rgba(239,68,68,0.18);border:1px solid #ef4444;border-radius:6px;padding:4px 10px;font-size:0.78rem;font-weight:700;color:#fca5a5;margin-bottom:4px;">
                    +{prob_high_delta:.1f}% High Risk Surge
                </div>
                <div style="font-size:0.72rem;color:#f87171;">
                    Low Confidence {prob_low_delta:.1f}%
                </div>
            </div>
            """)

        with flip_c3:
            render_html(f"""
            <div style="background:rgba(15, 23, 42, 0.85);border:1px solid rgba(239, 68, 68, 0.55);border-radius:12px;padding:18px;height:100%;box-shadow:0 0 20px rgba(239,68,68,0.2);">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                    <span style="font-size:0.78rem;font-weight:700;letter-spacing:1px;color:#fca5a5;">2. ATTACK INJECTED</span>
                    <span style="background:rgba(239,68,68,0.25);color:#ef4444;border:1px solid #ef4444;padding:3px 10px;border-radius:12px;font-size:0.75rem;font-weight:800;">
                        🔴 {pred_attack_label.upper()} RISK
                    </span>
                </div>
                <div style="font-size:1.35rem;font-weight:800;color:#ef4444;margin-bottom:8px;">
                    {probs_attack_map.get('High', 0.0)*100:.1f}% High Risk Confidence
                </div>
                <div style="font-size:0.82rem;color:#cbd5e1;line-height:1.7;">
                    <div>• 24h Cashout: <strong style="color:#ef4444;">₹{int(attack_scenario['total_withdrawal_amount']):,}</strong> (+₹6L Surge)</div>
                    <div>• Unusual Signals: <strong style="color:#ef4444;">{int(attack_scenario['unusual_activity_count'])}</strong> (15 card retries)</div>
                    <div>• Low-Risk Prob: <span style="color:#94a3b8;">{probs_attack_map.get('Low', 0.0)*100:.1f}%</span> (Collapsed)</div>
                    <div>• System State: <span style="color:#ef4444;font-weight:700;">🚨 RAPID DISPATCH REQUIRED</span></div>
                </div>
            </div>
            """)

        # Probability Delta Shift Grouped Bar Chart
        chart_df = pd.DataFrame([
            {"Scenario": "Baseline Normal", "Risk Class": "Low Risk", "Probability (%)": probs_base_map.get("Low", 0.0) * 100},
            {"Scenario": "Baseline Normal", "Risk Class": "Medium Risk", "Probability (%)": probs_base_map.get("Medium", 0.0) * 100},
            {"Scenario": "Baseline Normal", "Risk Class": "High Risk", "Probability (%)": probs_base_map.get("High", 0.0) * 100},
            {"Scenario": "⚡ Injected Attack", "Risk Class": "Low Risk", "Probability (%)": probs_attack_map.get("Low", 0.0) * 100},
            {"Scenario": "⚡ Injected Attack", "Risk Class": "Medium Risk", "Probability (%)": probs_attack_map.get("Medium", 0.0) * 100},
            {"Scenario": "⚡ Injected Attack", "Risk Class": "High Risk", "Probability (%)": probs_attack_map.get("High", 0.0) * 100},
        ])

        fig_flip = px.bar(
            chart_df,
            x="Risk Class",
            y="Probability (%)",
            color="Scenario",
            barmode="group",
            text=chart_df["Probability (%)"].apply(lambda v: f"{v:.1f}%"),
            color_discrete_map={
                "Baseline Normal": "#3b82f6",
                "⚡ Injected Attack": "#ef4444"
            },
            height=280,
            title="Real-Time Probability Shift: Baseline Normal vs. Injected Syndicate Attack"
        )
        fig_flip.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        fig_flip.update_traces(textposition="outside")
        st.plotly_chart(fig_flip, use_container_width=True)

        # Automated Incident Response Directives Matrix
        render_html("""
        <div style="background:rgba(15, 23, 42, 0.7);border:1px solid rgba(239,68,68,0.3);border-radius:10px;padding:14px 18px;margin-bottom:20px;">
            <div style="font-size:0.8rem;font-weight:700;letter-spacing:1px;color:#fca5a5;margin-bottom:8px;">
                ⚡ AUTOMATED SECURITY MITIGATION DIRECTIVES TRIGGERED
            </div>
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:10px;font-size:0.8rem;color:#cbd5e1;">
                <div style="background:rgba(239,68,68,0.1);border-left:3px solid #ef4444;padding:8px 10px;border-radius:4px;">
                    🔒 <strong>ATM Cash Cassette Solenoids:</strong> Locked remotely
                </div>
                <div style="background:rgba(245,158,11,0.1);border-left:3px solid #f59e0b;padding:8px 10px;border-radius:4px;">
                    📹 <strong>4K CCTV Stream:</strong> High-priority incident clip flagged
                </div>
                <div style="background:rgba(59,130,246,0.1);border-left:3px solid #3b82f6;padding:8px 10px;border-radius:4px;">
                    🚔 <strong>Cyber Patrol Unit:</strong> Auto-dispatched (ETA 5 mins)
                </div>
                <div style="background:rgba(168,85,247,0.1);border-left:3px solid #a855f7;padding:8px 10px;border-radius:4px;">
                    💳 <strong>Central Switch Gateway:</strong> Consecutive retries blocked
                </div>
            </div>
        </div>
        """)

    # 1-Click Scenario Preset Buttons
    st.markdown("#### ⚡ 1-Click Scenario Presets")
    st.caption("Click a preset to instantly populate realistic zone profiles without manual typing:")

    sc1, sc2, sc3, sc4 = st.columns(4)

    high_preset = {
        "zone_id": "ZONE_008", "state": "Delhi", "city": "South Delhi", "atm_count": 8.0,
        "withdrawal_count": 142.0, "avg_withdrawal_amount": 4200.0, "total_withdrawal_amount": 596400.0,
        "unusual_activity_count": 8.0, "withdrawals_sum_7d": 890.0, "unusual_activity_sum_7d": 45.0,
        "incidents_sum_7d": 5.0, "withdrawals_sum_30d": 3800.0, "unusual_activity_sum_30d": 180.0,
        "incidents_sum_30d": 19.0, "month": 11, "day_of_week": 5, "is_weekend": 1
    }

    low_preset = {
        "zone_id": "ZONE_017", "state": "Maharashtra", "city": "Pune", "atm_count": 12.0,
        "withdrawal_count": 48.0, "avg_withdrawal_amount": 2100.0, "total_withdrawal_amount": 100800.0,
        "unusual_activity_count": 0.0, "withdrawals_sum_7d": 310.0, "unusual_activity_sum_7d": 3.0,
        "incidents_sum_7d": 0.0, "withdrawals_sum_30d": 1400.0, "unusual_activity_sum_30d": 12.0,
        "incidents_sum_30d": 1.0, "month": 3, "day_of_week": 2, "is_weekend": 0
    }

    med_preset = {
        "zone_id": "ZONE_001", "state": "Punjab", "city": "Ludhiana", "atm_count": 10.0,
        "withdrawal_count": 82.0, "avg_withdrawal_amount": 3100.0, "total_withdrawal_amount": 254200.0,
        "unusual_activity_count": 2.0, "withdrawals_sum_7d": 560.0, "unusual_activity_sum_7d": 15.0,
        "incidents_sum_7d": 2.0, "withdrawals_sum_30d": 2400.0, "unusual_activity_sum_30d": 60.0,
        "incidents_sum_30d": 6.0, "month": 6, "day_of_week": 3, "is_weekend": 0
    }

    median_preset = {
        f: float(df[f].median()) if pd.api.types.is_numeric_dtype(df[f]) else df[f].mode().iloc[0]
        for f in ["atm_count", "withdrawal_count", "avg_withdrawal_amount", "total_withdrawal_amount",
                 "unusual_activity_count", "withdrawals_sum_7d", "unusual_activity_sum_7d",
                 "incidents_sum_7d", "withdrawals_sum_30d", "unusual_activity_sum_30d",
                 "incidents_sum_30d", "month", "day_of_week", "is_weekend"]
    }
    median_preset["zone_id"] = "ZONE_001"

    if "current_preset" not in st.session_state:
        st.session_state["current_preset"] = median_preset

    with sc1:
        if st.button("🚨 Load High-Risk Fraud Scenario", use_container_width=True):
            st.session_state["current_preset"] = high_preset
            st.rerun()
    with sc2:
        if st.button("🛡️ Load Low-Risk Normal Scenario", use_container_width=True):
            st.session_state["current_preset"] = low_preset
            st.rerun()
    with sc3:
        if st.button("⚖️ Load Medium-Risk Baseline", use_container_width=True):
            st.session_state["current_preset"] = med_preset
            st.rerun()
    with sc4:
        if st.button("🔄 Reset to Dataset Medians", use_container_width=True):
            st.session_state["current_preset"] = median_preset
            st.rerun()

    if attack_injected:
        active_vals = attack_preset
    else:
        active_vals = st.session_state["current_preset"]

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("single_prediction_form"):
        col_grp1, col_grp2, col_grp3 = st.columns(3)

        with col_grp1:
            st.markdown("##### 📍 Zone & Calendar Context")
            zone_choice = st.selectbox(
                "ATM Zone",
                sorted(df["zone_id"].unique().tolist()),
                index=sorted(df["zone_id"].unique().tolist()).index(active_vals.get("zone_id", "ZONE_001"))
            )
            zone_row = df[df["zone_id"] == zone_choice].iloc[0]
            lat_val = float(zone_row["latitude"])
            lon_val = float(zone_row["longitude"])
            st.caption(f"Coordinates: `{lat_val:.3f}°N, {lon_val:.3f}°E` ({zone_row['city']}, {zone_row['state']})")

            month_val = st.slider("Month of Year", 1, 12, int(active_vals.get("month", 6)))
            dow_val = st.slider("Day of Week (0=Mon, 6=Sun)", 0, 6, int(active_vals.get("day_of_week", 2)))
            weekend_val = st.selectbox("Is Weekend?", [0, 1], index=int(active_vals.get("is_weekend", 0)))

        with col_grp2:
            st.markdown("##### 🏧 ATM Activity (Last 24h)")
            atm_cnt = st.number_input("ATM Count in Zone", 1.0, 50.0, float(active_vals.get("atm_count", 10.0)), step=1.0)
            withd_cnt = st.number_input("Withdrawal Count", 0.0, 500.0, float(active_vals.get("withdrawal_count", 80.0)), step=5.0)
            avg_amt = st.number_input("Avg Withdrawal Amount (₹)", 500.0, 25000.0, float(active_vals.get("avg_withdrawal_amount", 3000.0)), step=200.0)
            tot_amt = st.number_input("Total Withdrawal Amount (₹)", 0.0, 2000000.0, float(active_vals.get("total_withdrawal_amount", withd_cnt * avg_amt)), step=10000.0)
            unusual_cnt = st.number_input("Unusual Activity Signals", 0.0, 50.0, float(active_vals.get("unusual_activity_count", 1.0)), step=1.0)

        with col_grp3:
            st.markdown("##### 📈 Historical Rolling Trends")
            w7d = st.number_input("7-Day Withdrawals Sum", 0.0, 5000.0, float(active_vals.get("withdrawals_sum_7d", 500.0)), step=20.0)
            u7d = st.number_input("7-Day Unusual Activity Sum", 0.0, 200.0, float(active_vals.get("unusual_activity_sum_7d", 10.0)), step=2.0)
            inc7d = st.number_input("7-Day Incident Count Sum", 0.0, 50.0, float(active_vals.get("incidents_sum_7d", 2.0)), step=1.0)
            w30d = st.number_input("30-Day Withdrawals Sum", 0.0, 20000.0, float(active_vals.get("withdrawals_sum_30d", 2200.0)), step=50.0)
            u30d = st.number_input("30-Day Unusual Activity Sum", 0.0, 1000.0, float(active_vals.get("unusual_activity_sum_30d", 40.0)), step=5.0)
            inc30d = st.number_input("30-Day Incident Count Sum", 0.0, 150.0, float(active_vals.get("incidents_sum_30d", 5.0)), step=1.0)

        submit_btn = st.form_submit_button("🔍 Compute 7-Day Risk Forecast", use_container_width=True)

    if submit_btn:
        w_per_atm = withd_cnt / (atm_cnt if atm_cnt > 0 else 1.0)
        unusual_ratio = unusual_cnt / (withd_cnt if withd_cnt > 0 else 1.0)
        daily_inc_30d = inc30d / 30.0
        amt_per_atm = tot_amt / (atm_cnt if atm_cnt > 0 else 1.0)
        season_sin = 0.0
        season_cos = 1.0

        sample_dict = {
            "zone_id": zone_choice,
            "latitude": lat_val,
            "longitude": lon_val,
            "day_of_week": dow_val,
            "month": month_val,
            "is_weekend": weekend_val,
            "atm_count": atm_cnt,
            "withdrawal_count": withd_cnt,
            "avg_withdrawal_amount": avg_amt,
            "total_withdrawal_amount": tot_amt,
            "unusual_activity_count": unusual_cnt,
            "withdrawals_sum_7d": w7d,
            "unusual_activity_sum_7d": u7d,
            "incidents_sum_7d": inc7d,
            "withdrawals_sum_30d": w30d,
            "unusual_activity_sum_30d": u30d,
            "incidents_sum_30d": inc30d,
            "withdrawals_per_atm": w_per_atm,
            "unusual_activity_ratio": unusual_ratio,
            "avg_daily_incidents_30d": daily_inc_30d,
            "withdrawal_amount_per_atm": amt_per_atm,
            "season_30d_sin": season_sin,
            "season_30d_cos": season_cos
        }

        eval_df = pd.DataFrame([sample_dict])[FEATURES]
        pred_label = model.predict(eval_df)[0]
        pred_probs = model.predict_proba(eval_df)[0]

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🎯 Inference Results (7-Day Forward Model Estimate)")
        st.caption(
            "Note: Class probabilities below are statistical model estimates for the next 7 days (t+1 to t+7) "
            "based on synthetic zone-day patterns, not confirmed real-world crime incidents."
        )

        res_c1, res_c2 = st.columns([1.2, 1.8])

        with res_c1:
            if pred_label == "High":
                st.error("### 🔴 Predicted Risk: HIGH RISK")
                rec_text = "Urgent: Elevated 7-day incident probability estimated for this zone. Recommend scheduling ATM telemetry audits and reviewing monitoring coverage."
            elif pred_label == "Medium":
                st.warning("### 🟠 Predicted Risk: MEDIUM RISK")
                rec_text = "Caution: Moderate risk pattern estimated. Increase remote sensor monitoring and track consecutive unusual activity signals."
            else:
                st.success("### 🟢 Predicted Risk: LOW RISK")
                rec_text = "Normal: Routine transactional behavior estimated. Standard automated monitoring is sufficient."

            st.info(f"**Recommended Action (Prototype Advisory):**\n{rec_text}")

        with res_c2:
            prob_df = pd.DataFrame({
                "Risk Category": model.classes_,
                "Probability (%)": pred_probs * 100.0
            })

            fig_prob = px.bar(
                prob_df,
                x="Risk Category",
                y="Probability (%)",
                color="Risk Category",
                color_discrete_map=risk_colors,
                text=prob_df["Probability (%)"].apply(lambda v: f"{v:.1f}%"),
                height=260,
                title="Estimated Class Probabilities (Next 7 Days)"
            )
            fig_prob.update_layout(margin=dict(l=10, r=10, t=35, b=10), yaxis_range=[0, 100])
            st.plotly_chart(fig_prob, use_container_width=True)

        # Dynamic Local Feature Attribution for the Current Input Row
        try:
            preproc = model.named_steps["preprocessor"]
            clf = model.named_steps["classifier"]
            x_trans = preproc.transform(eval_df)
            if hasattr(x_trans, "toarray"):
                x_trans = x_trans.toarray()
            feat_names_out = [
                n.replace("numeric__", "").replace("categorical__", "")
                for n in preproc.get_feature_names_out()
            ]
            class_idx = list(model.classes_).index(pred_label)
            contrib = x_trans[0] * clf.coef_[class_idx]
            contrib_df = pd.DataFrame({
                "Feature": feat_names_out,
                "Contribution": contrib
            })
            contrib_df["Abs"] = contrib_df["Contribution"].abs()
            top_contrib = contrib_df[contrib_df["Abs"] > 1e-4].sort_values("Abs", ascending=True).tail(10)

            st.markdown("#### 🧠 Live Local Feature Contributions for This Prediction")
            st.caption(
                f"Exact linear log-odds contributions of your input values toward the predicted **{pred_label} Risk** class "
                "(positive bars push toward this class; negative bars oppose it)."
            )
            fig_local = go.Figure(go.Bar(
                x=top_contrib["Contribution"],
                y=top_contrib["Feature"],
                orientation="h",
                marker_color=[
                    "#ef4444" if (pred_label == "High" and v > 0) else ("#22c55e" if v > 0 else "#64748b")
                    for v in top_contrib["Contribution"]
                ],
                text=top_contrib["Contribution"].apply(lambda v: f"{v:+.3f}"),
                textposition="outside"
            ))
            fig_local.update_layout(
                height=310,
                margin=dict(l=10, r=40, t=20, b=10),
                xaxis_title=f"Log-Odds Contribution Toward '{pred_label}' Class",
                yaxis_title=""
            )
            st.plotly_chart(fig_local, use_container_width=True)
        except Exception:
            pass


# --------------------------------------------------
# 3. BATCH CSV PREDICTION
# --------------------------------------------------

elif page == "📁 Batch CSV Prediction":

    render_html("""
    <div style="background: linear-gradient(135deg, #090d16 0%, #312e81 100%);
                border: 1px solid rgba(99, 102, 241, 0.35);
                border-radius: 14px;
                padding: 24px 28px;
                margin-bottom: 22px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);">
        <h1 style="color:white;margin:0;font-size:1.9rem;font-weight:700;">
            Batch Cybercrime Risk Forecasting
        </h1>
        <p style="color:#c7d2fe;margin:6px 0 0 0;font-size:1rem;">
            Upload raw or processed zone-day CSV batches, validate schema & data types, and export 7-day risk predictions.
        </p>
    </div>
    """)

    def prepare_and_validate_batch(raw_batch: pd.DataFrame):
        """
        Validates an uploaded batch DataFrame and automatically engineers derived features
        if raw zone-day columns are provided. Returns (prepared_df, warnings_list, error_msg).
        """
        if raw_batch is None or len(raw_batch) == 0:
            return None, [], "The uploaded CSV file is empty (0 rows). Please provide at least one zone-day record."

        work_df = raw_batch.copy()
        notes = []

        # Base columns required before derived feature computation
        base_required = [
            "zone_id", "latitude", "longitude", "day_of_week", "month", "is_weekend",
            "atm_count", "withdrawal_count", "avg_withdrawal_amount",
            "total_withdrawal_amount", "unusual_activity_count",
            "withdrawals_sum_7d", "unusual_activity_sum_7d", "incidents_sum_7d",
            "withdrawals_sum_30d", "unusual_activity_sum_30d", "incidents_sum_30d"
        ]
        missing_base = [c for c in base_required if c not in work_df.columns]
        if missing_base:
            return None, [], f"Missing required base columns in CSV: {', '.join(missing_base)}"

        # Coerce numeric base columns safely
        num_base = [c for c in base_required if c != "zone_id"]
        for col in num_base:
            coerced = pd.to_numeric(work_df[col], errors="coerce")
            invalid_cnt = int(coerced.isna().sum() - work_df[col].isna().sum())
            if invalid_cnt > 0:
                notes.append(f"Column `{col}` had {invalid_cnt} non-numeric cell(s) coerced to NaN (imputed via pipeline median).")
            work_df[col] = coerced

        # Auto-compute the 6 engineered features if missing
        derived_cols = [
            "withdrawals_per_atm", "unusual_activity_ratio",
            "avg_daily_incidents_30d", "withdrawal_amount_per_atm",
            "season_30d_sin", "season_30d_cos"
        ]
        missing_derived = [c for c in derived_cols if c not in work_df.columns]
        if missing_derived:
            atm_safe = work_df["atm_count"].replace(0, np.nan)
            withd_safe = work_df["withdrawal_count"].replace(0, np.nan)
            work_df["withdrawals_per_atm"] = work_df["withdrawal_count"] / atm_safe
            work_df["unusual_activity_ratio"] = work_df["unusual_activity_count"] / withd_safe
            work_df["avg_daily_incidents_30d"] = work_df["incidents_sum_30d"] / 30.0
            work_df["withdrawal_amount_per_atm"] = work_df["total_withdrawal_amount"] / atm_safe

            if "date" in work_df.columns:
                parsed_dates = pd.to_datetime(work_df["date"], errors="coerce")
                day_idx = (parsed_dates - pd.Timestamp("2025-01-01")).dt.days.fillna(0)
            else:
                day_idx = pd.Series(np.arange(len(work_df)), index=work_df.index)
            work_df["season_30d_sin"] = np.sin(2 * np.pi * day_idx / 30.0)
            work_df["season_30d_cos"] = np.cos(2 * np.pi * day_idx / 30.0)
            notes.append(f"Automatically computed {len(missing_derived)} derived feature(s): {', '.join(missing_derived)}.")

        work_df = work_df.replace([np.inf, -np.inf], np.nan)
        return work_df, notes, None

    # 1-Click Test Button
    st.markdown("#### ⚡ Quick Actions")
    bt_c1, bt_c2 = st.columns([1.5, 1.5])

    use_sample = False
    with bt_c1:
        if st.button("📋 Test with Sample Processed Dataset (1-Click)", use_container_width=True):
            use_sample = True

    with bt_c2:
        if BATCH_SAMPLE_PATH.exists():
            sample_bytes = pd.read_csv(BATCH_SAMPLE_PATH).head(50).to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download CSV Template (50 Sample Rows)",
                data=sample_bytes,
                file_name="batch_sample_template.csv",
                mime="text/csv",
                use_container_width=True
            )

    uploaded_file = st.file_uploader(
        "Or Upload Your Custom CSV File (Raw or Processed Zone-Day Format)",
        type=["csv"],
        help="Upload a CSV with either all 23 model features or the 17 raw zone-day columns (derived features will be auto-computed)."
    )

    df_to_predict = None
    if use_sample and BATCH_SAMPLE_PATH.exists():
        df_to_predict = pd.read_csv(BATCH_SAMPLE_PATH).head(300)
        st.success("Loaded 300 records from verified batch sample dataset (`data/processed/batch_prediction_sample.csv`).")
    elif uploaded_file is not None:
        try:
            df_to_predict = pd.read_csv(uploaded_file)
            st.success(f"Uploaded CSV file `{uploaded_file.name}` with {len(df_to_predict)} rows and {len(df_to_predict.columns)} columns.")
        except Exception as e:
            st.error(f"Error parsing uploaded CSV file: {e}")

    if df_to_predict is not None:
        valid_df, batch_notes, err_msg = prepare_and_validate_batch(df_to_predict)
        for note in batch_notes:
            st.info(f"ℹ️ {note}")

        if err_msg:
            st.error(f"❌ Validation Error: {err_msg}")
        else:
            with st.spinner("Executing model inference on batch..."):
                batch_preds = model.predict(valid_df[FEATURES])
                batch_probs = model.predict_proba(valid_df[FEATURES])

                out_df = valid_df.copy()
                out_df["Predicted_Risk"] = batch_preds
                for i, cl in enumerate(model.classes_):
                    out_df[f"Probability_{cl}_pct"] = (batch_probs[:, i] * 100.0).round(2)

            st.markdown("### 📊 Batch Prediction Summary")
            b_high = int((out_df["Predicted_Risk"] == "High").sum())
            b_med = int((out_df["Predicted_Risk"] == "Medium").sum())
            b_low = int((out_df["Predicted_Risk"] == "Low").sum())

            sum_c1, sum_c2, sum_c3, sum_c4 = st.columns(4)
            sum_c1.metric("Total Records Evaluated", len(out_df))
            sum_c2.metric("🔴 High Risk Forecasts", f"{b_high}", f"{(b_high/len(out_df))*100:.1f}%")
            sum_c3.metric("🟠 Medium Risk Forecasts", f"{b_med}", f"{(b_med/len(out_df))*100:.1f}%")
            sum_c4.metric("🟢 Low Risk Forecasts", f"{b_low}", f"{(b_low/len(out_df))*100:.1f}%")

            st.markdown("#### 📋 Prediction Results Preview (First 100 Rows)")
            preview_cols = [c for c in ["zone_id", "date", "state", "city", "Predicted_Risk", "Probability_High_pct", "Probability_Medium_pct", "Probability_Low_pct"] if c in out_df.columns]
            other_cols = [c for c in out_df.columns if c not in preview_cols]
            st.dataframe(out_df[preview_cols + other_cols].head(100), use_container_width=True)

            out_csv = out_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download Complete Batch Predictions (CSV)",
                data=out_csv,
                file_name="batch_risk_predictions.csv",
                mime="text/csv",
                use_container_width=True
            )


# --------------------------------------------------
# 4. MODEL INTELLIGENCE & EXPLAINABILITY
# --------------------------------------------------

elif page == "ℹ️ Model Intelligence & Explainability":

    render_html("""
    <div style="background: linear-gradient(135deg, #090d16 0%, #581c87 100%);
                border: 1px solid rgba(168, 85, 247, 0.35);
                border-radius: 14px;
                padding: 24px 28px;
                margin-bottom: 22px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);">
        <h1 style="color:white;margin:0;font-size:1.9rem;font-weight:700;">
            Model Architecture, Evaluation & Explainable AI
        </h1>
        <p style="color:#ddd6fe;margin:6px 0 0 0;font-size:1rem;">
            Supervised learning benchmark, time-aware cross-validation, held-out test metrics, SHAP global attributions, and LIME local explanations.
        </p>
    </div>
    """)

    if RESULTS_PATH.exists():
        metrics_df = pd.read_csv(RESULTS_PATH)
        best_row = metrics_df[metrics_df["Model"].str.contains("Logistic", case=False, na=False)].iloc[0]

        st.markdown("### 🏆 Selected Production Classifier (Held-Out Test Set: N = 3,030)")
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Selected Model", "Logistic Reg.")
        m2.metric("Test Accuracy", f"{float(best_row['Accuracy'])*100:.2f}%")
        m3.metric("Balanced Acc.", f"{float(best_row['Balanced Accuracy'])*100:.2f}%")
        m4.metric("Macro Precision", f"{float(best_row['Precision (macro)'])*100:.2f}%")
        m5.metric("Macro F1-Score", f"{float(best_row['F1 (macro)'])*100:.2f}%")
        m6.metric("ROC-AUC (Macro)", f"{float(best_row['ROC-AUC (OVR macro)'])*100:.2f}%")

        st.info(
            "**Academic Performance Interpretation:** Logistic Regression was selected via 5-fold time-aware cross-validation "
            "(Best CV Macro F1 = 44.35%). On the held-out test period (`2026-03-09` to `2026-06-17`), it achieves **42.05% Macro F1** "
            "(more than doubling the Majority-Class Baseline Macro F1 of **20.77%**). Overall accuracy (**46.96%**) and ROC-AUC (**59.98%**) "
            "are modest due to the inherent stochasticity of synthetic Poisson incident generation. This system is an academic prototype."
        )

    tab_exp1, tab_exp2, tab_exp3 = st.tabs([
        "🧠 SHAP & LIME Explainability",
        "📉 Confusion Matrix & Classification Report",
        "⚙️ Model Metadata & Cross-Validation Benchmarks"
    ])

    with tab_exp1:
        exp_c1, exp_c2 = st.columns(2)
        with exp_c1:
            st.markdown("#### Global Feature Attribution (SHAP)")
            st.caption("Ranks the 23 input features by mean absolute impact on High-Risk predictions across held-out test records.")
            if SHAP_PATH.exists():
                st.image(str(SHAP_PATH), use_container_width=True, caption="SHAP Summary Plot for High-Risk Class (notebooks/04_explainable_ai.ipynb)")
            else:
                st.info("SHAP plot available in `notebooks/04_explainable_ai.ipynb`.")

        with exp_c2:
            st.markdown("#### Local Instance Explanation (LIME)")
            st.caption("Explains an individual High-Risk zone-day prediction by showing supporting (green) vs. opposing (red) feature rules.")
            if LIME_PATH.exists():
                st.image(str(LIME_PATH), use_container_width=True, caption="LIME Local Explanation for a High-Risk Zone-Day Instance")
            else:
                st.info("LIME explanation available in `notebooks/04_explainable_ai.ipynb`.")

    with tab_exp2:
        cm_col1, cm_col2 = st.columns(2)
        with cm_col1:
            if CONFUSION_PATH.exists():
                cm_df = pd.read_csv(CONFUSION_PATH, index_col=0)
                st.markdown("#### Held-Out Test Set Confusion Matrix (N = 3,030)")
                st.dataframe(cm_df, use_container_width=True)
                st.caption("548 of 1,037 High-Risk instances (52.84% Recall) and 761 of 1,371 Medium-Risk instances (55.51% Recall) were correctly identified.")
        with cm_col2:
            rep_path = ROOT / "results" / "phase4_best_model_classification_report.csv"
            if rep_path.exists():
                rep_df = pd.read_csv(rep_path, index_col=0)
                st.markdown("#### Per-Class Classification Report")
                st.dataframe(rep_df.style.format("{:.4f}"), use_container_width=True)

        if RESULTS_PATH.exists():
            st.markdown("#### Held-Out Test Set Benchmark Comparison (`results/phase4_test_metrics.csv`)")
            st.dataframe(pd.read_csv(RESULTS_PATH), use_container_width=True, hide_index=True)

    with tab_exp3:
        cv_path = ROOT / "results" / "phase4_cv_comparison.csv"
        p3_path = ROOT / "results" / "classification_model_comparison.csv"
        if cv_path.exists():
            st.markdown("#### Phase 4: 5-Fold Time-Aware Cross-Validation Tuning Results")
            st.dataframe(pd.read_csv(cv_path), use_container_width=True, hide_index=True)
        if p3_path.exists():
            st.markdown("#### Phase 3: Initial 6-Algorithm Benchmark Comparison")
            st.dataframe(pd.read_csv(p3_path), use_container_width=True, hide_index=True)

        st.markdown("#### Saved Model Bundle Metadata (`models/best_risk_classifier.joblib`)")
        st.json({
            "Selected Classifier": str(model.named_steps["classifier"]),
            "Target Column": TARGET,
            "Class Order": CLASS_ORDER,
            "Forecast Horizon (Days)": bundle.get("forecast_horizon_days", 7),
            "Forecast Timing": bundle.get("forecast_timing", "next_7_days"),
            "Dataset Type": bundle.get("dataset_type", "synthetic_academic"),
            "Input FeaturesCount": len(FEATURES),
            "Input Features": FEATURES
        })


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
render_html("""
<div style="display:flex;justify-content:space-between;color:#64748b;font-size:0.85rem;padding:8px 0;">
    <div>🛡️ Cybercrime Cash-Withdrawal Location Forecast · Academic Research Demonstration</div>
    <div>Strictly Synthetic Data · Continuous Live Telemetry Pipeline</div>
</div>
""")
