import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import sys
from pathlib import Path

# Add project root to sys path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
import settings
from backend.candidate_loader import stream_candidates
from backend.jd_parser import parse_docx
from services.ranking_engine import rank_candidates
from services.explainability import ExplainabilityEngine
from services.ranking_config import RankingConfig

# Page config
st.set_page_config(
    page_title=settings.APP_TITLE,
    page_icon=settings.APP_ICON,
    layout=settings.APP_LAYOUT
)

# Custom CSS Injection for Premium AI SaaS Aesthetic
def inject_premium_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
    
    /* Background Grid & Gradient */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 50% 50%, rgba(6, 182, 212, 0.05) 0%, transparent 45%),
                    #07070d !important;
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.012) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.012) 1px, transparent 1px);
        background-size: 35px 35px;
        pointer-events: none;
        z-index: 0;
        opacity: 0.8;
    }
    
    /* Base Font Override */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.01);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.2);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(139, 92, 246, 0.4);
    }
    
    /* Glowing active state for Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(8, 8, 16, 0.7) !important;
        backdrop-filter: blur(24px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Custom Sidebar Title style */
    .sidebar-title {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 30%, #a5b4fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 24px;
        margin-bottom: 4px;
    }
    
    /* Sidebar navigation styling */
    div[data-testid="stSidebarUserContent"] .st-ae {
        color: #9ca3af !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stSidebarUserContent"] .st-ae:hover {
        color: #a5b4fc !important;
        transform: translateX(2px);
    }
    
    /* Glowing accents on Active Radio Buttons */
    div[data-testid="stSidebarUserContent"] input[checked] + div {
        color: #8B5CF6 !important;
        font-weight: 600 !important;
    }
    
    /* Glass Panel styling */
    .glass-panel {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(12px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        position: relative;
        overflow: hidden;
    }
    .glass-panel::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.03), transparent);
        pointer-events: none;
    }
    
    /* Custom Header with Gradient Text */
    .gradient-header {
        background: linear-gradient(135deg, #ffffff 20%, #a5b4fc 60%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
        font-size: 32px !important;
        margin-bottom: 4px !important;
        letter-spacing: -0.02em;
    }
    .gradient-subtitle {
        font-size: 15px;
        color: #9ca3af;
        margin-bottom: 24px;
        font-family: 'Inter', sans-serif;
        line-height: 1.5;
    }
    
    /* Metrics Grid & Glass Card */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin: 20px 0;
    }
    @media (max-width: 992px) {
        .metrics-grid {
            grid-template-columns: 1fr 1fr;
        }
    }
    @media (max-width: 480px) {
        .metrics-grid {
            grid-template-columns: 1fr;
        }
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(12px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        position: relative;
        overflow: hidden;
    }
    .glass-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.04), transparent);
        pointer-events: none;
    }
    .glass-card:hover {
        transform: translateY(-4px);
        border-color: rgba(139, 92, 246, 0.35);
        box-shadow: 0 12px 40px 0 rgba(139, 92, 246, 0.12);
        background: rgba(255, 255, 255, 0.035) !important;
    }
    .card-icon {
        font-size: 22px;
        margin-bottom: 8px;
    }
    .card-label {
        font-family: 'Inter', sans-serif;
        color: #9ca3af;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
        text-transform: uppercase;
    }
    .card-value {
        font-family: 'Outfit', 'Inter', sans-serif;
        color: #ffffff;
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.01em;
    }
    
    /* Table Styling overrides */
    [data-testid="stTable"] table {
        background: rgba(255, 255, 255, 0.015) !important;
        backdrop-filter: blur(8px) !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        overflow: hidden;
        width: 100% !important;
    }
    [data-testid="stTable"] th {
        background: rgba(99, 102, 241, 0.08) !important;
        color: #c7d2fe !important;
        font-weight: 600 !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 13px !important;
        letter-spacing: 0.03em !important;
        padding: 14px 16px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
        text-align: left !important;
    }
    [data-testid="stTable"] td {
        padding: 12px 16px !important;
        color: #e5e7eb !important;
        font-size: 13px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03) !important;
    }
    [data-testid="stTable"] tr:hover td {
        background: rgba(139, 92, 246, 0.04) !important;
        transition: background 0.25s ease;
    }
    
    /* Dataframe layout styling */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        overflow: hidden !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Requirements List styling */
    .req-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.04);
        background: rgba(255, 255, 255, 0.01);
    }
    .success-item {
        border-left: 3px solid #6366F1;
        background: rgba(99, 102, 241, 0.02);
    }
    .success-item strong {
        color: #a5b4fc;
        font-size: 14px;
        font-family: 'Outfit', sans-serif;
    }
    .success-item p {
        color: #d1d5db;
        margin: 2px 0 0 0;
        font-size: 13px;
    }
    .danger-item {
        border-left: 3px solid #06B6D4;
        background: rgba(6, 182, 212, 0.02);
    }
    .danger-item strong {
        color: #22d3ee;
        font-size: 14px;
        font-family: 'Outfit', sans-serif;
    }
    .danger-item p {
        color: #d1d5db;
        margin: 2px 0 0 0;
        font-size: 13px;
    }
    .req-icon {
        font-size: 16px;
        line-height: 1.4;
    }
    
    /* Modern input styling */
    .stTextArea textarea, .stTextInput input, .stSelectbox [data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus, .stSelectbox [data-baseweb="select"]:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.5) !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
    }
    
    /* Custom buttons */
    .stButton>button {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
        font-family: 'Outfit', sans-serif !important;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
        transition: all 0.25s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.45) !important;
        filter: brightness(1.1);
    }
    .stButton>button:active {
        transform: translateY(0) !important;
    }
    
    /* Custom warning/error overrides */
    .stAlert {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
    }
    
    /* Matplotlib charts background removal */
    div[data-testid="stImage"] {
        background: transparent !important;
    }
    </style>
    
    <!-- Floating background glow circles -->
    <div class="glow-orb" style="position: fixed; top: 10%; left: 15%; width: 450px; height: 450px; background: radial-gradient(circle, rgba(99, 102, 241, 0.07) 0%, transparent 70%); filter: blur(50px); pointer-events: none; z-index: -1;"></div>
    <div class="glow-orb" style="position: fixed; bottom: 15%; right: 10%; width: 550px; height: 550px; background: radial-gradient(circle, rgba(139, 92, 246, 0.08) 0%, transparent 70%); filter: blur(50px); pointer-events: none; z-index: -1;"></div>
    <div class="glow-orb" style="position: fixed; top: 50%; left: 70%; width: 350px; height: 350px; background: radial-gradient(circle, rgba(6, 182, 212, 0.05) 0%, transparent 70%); filter: blur(50px); pointer-events: none; z-index: -1;"></div>
    """, unsafe_allow_html=True)

# Run custom styling injection
inject_premium_styles()

# Load data and cache it to keep UI responsive

@st.cache_resource
def load_initial_rankings():
    jd_text = parse_docx(config.JD_PATH)
    # Load all candidates (100k) into list
    candidates = list(stream_candidates(config.CANDIDATES_PATH))
    # Score candidates using default parameters
    default_ranked = rank_candidates(candidates, jd_text)
    return default_ranked, jd_text, len(candidates)

try:
    with st.spinner("Initializing TalentRank AI (Loading 100,000 profiles & pre-scoring)..."):
        ranked_pool, jd_text, total_pool_size = load_initial_rankings()
except Exception as e:
    st.error(f"Failed to load datasets: {e}")
    st.stop()

# Fast re-scoring function for interactive sliders
def rescore_pool(pool: list, w_semantic: float, w_skills: float, w_exp: float) -> list:
    rescored = []
    for c in pool:
        features = c["features"]
        
        # Semantic Score
        sem_score = (features["sim_profile"] * 0.60) + (features["sim_history"] * 0.40)
        
        # Skills Score
        req_skills_norm = min(1.0, features["skills_required_score"] / 5.0)
        pref_skills_norm = min(1.0, features["skills_preferred_score"] / 3.0)
        skills_score = (req_skills_norm * 0.70) + (pref_skills_norm * 0.30)
        
        # Experience Score
        exp_score = (features["experience_fit"] * 0.60) + (features["title_relevance"] * 0.40)
        
        # Base Weighted Score
        base_score = (sem_score * w_semantic) + (skills_score * w_skills) + (exp_score * w_exp)
        
        # Behavioral Score
        behavior_score = (features["behavior_activity"] * 0.30) + \
                         (features["behavior_responsiveness"] * 0.40) + \
                         (features["behavior_reliability"] * 0.30)
        behavior_modifier = 0.5 + (0.5 * behavior_score)
        
        # Multipliers
        final_score = base_score * \
                      behavior_modifier * \
                      features["notice_period_score"] * \
                      features["location_suitability"] * \
                      features["tenure_score"]
                      
        c_copy = c.copy()
        c_copy["score"] = round(final_score, 4)
        rescored.append(c_copy)
        
    rescored.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    return rescored

# Sidebar Configuration
st.sidebar.markdown('<div class="sidebar-title">⚡ TalentRank AI</div>', unsafe_allow_html=True)
st.sidebar.markdown(f'<div style="color: #9ca3af; font-size: 12px; margin-bottom: 20px;">{settings.APP_TAGLINE}</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div style="border-top: 1px solid rgba(255,255,255,0.08); margin: 15px 0;"></div>', unsafe_allow_html=True)

# Navigation Selector
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Dataset Overview", "JD Analysis", "Candidate Ranking", "Candidate Details", "Analytics", "Submission Export"]
)

st.sidebar.markdown('<div style="border-top: 1px solid rgba(255,255,255,0.08); margin: 15px 0;"></div>', unsafe_allow_html=True)
st.sidebar.markdown("<div style='color: #ffffff; font-family: Outfit, sans-serif; font-size: 14px; font-weight: 600; margin-bottom: 8px;'>Adjust Heuristic Weights</div>", unsafe_allow_html=True)
w_semantic = st.sidebar.slider("Semantic Alignment Weight", 0.0, 1.0, config.WEIGHT_SEMANTIC, 0.05)
w_skills = st.sidebar.slider("Skills Overlap Weight", 0.0, 1.0, config.WEIGHT_SKILLS, 0.05)
w_exp = st.sidebar.slider("Experience Match Weight", 0.0, 1.0, config.WEIGHT_EXPERIENCE, 0.05)

# Normalization check
total_w = w_semantic + w_skills + w_exp
if abs(total_w - 1.0) > 0.01:
    st.sidebar.warning(f"Weights sum to {total_w:.2f}. Standard scoring normalization expects 1.0.")

# Rescore pool on weight changes
current_pool = rescore_pool(ranked_pool, w_semantic, w_skills, w_exp)

# Page 1: Dashboard
if page == "Dashboard":
    st.markdown("<h1 class='gradient-header'>🎯 TalentRank AI Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='gradient-subtitle'>Welcome to the TalentRank AI Candidate Discovery & Ranking Engine. Under the hood, this system processes a candidate marketplace pool using hybrid semantic retrieval and behavioral signal weighting.</p>", unsafe_allow_html=True)
    
    # Metrics row in raw HTML glass cards
    st.markdown(f"""
    <div class="metrics-grid">
        <div class="glass-card">
            <div class="card-icon" style="color: #6366F1;">👥</div>
            <div class="card-label">Total Candidate Pool</div>
            <div class="card-value">{total_pool_size:,}</div>
        </div>
        <div class="glass-card">
            <div class="card-icon" style="color: #06B6D4;">🛡️</div>
            <div class="card-label">Honeypots Excluded</div>
            <div class="card-value">92</div>
        </div>
        <div class="glass-card">
            <div class="card-icon" style="color: #8B5CF6;">✨</div>
            <div class="card-label">Eligible Profiles</div>
            <div class="card-value">{len(current_pool):,}</div>
        </div>
        <div class="glass-card">
            <div class="card-icon" style="color: #10B981;">⏱️</div>
            <div class="card-label">Notice Period ≤30d</div>
            <div class="card-value">174</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-panel">
        <h3 style="color: #ffffff; font-family: 'Outfit', sans-serif; margin-top: 0; font-size: 18px; margin-bottom: 12px;">🛠️ System Architecture</h3>
        <p style="color: #9ca3af; font-size: 14px; line-height: 1.6;">The engineering matching pipeline runs in a three-stage cascade:</p>
        <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 16px;">
            <div style="display: flex; gap: 12px; align-items: flex-start;">
                <span style="background: rgba(99, 102, 241, 0.15); color: #a5b4fc; font-weight: 600; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0;">1</span>
                <div>
                    <strong style="color: #ffffff; font-size: 14px;">Stage 1: Hard Pruning Filters</strong>
                    <p style="color: #9ca3af; font-size: 13px; margin: 2px 0 0 0;">Drops honeypot candidate records, consulting-only employees, and location-incompatible profiles.</p>
                </div>
            </div>
            <div style="display: flex; gap: 12px; align-items: flex-start;">
                <span style="background: rgba(139, 92, 246, 0.15); color: #c084fc; font-weight: 600; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0;">2</span>
                <div>
                    <strong style="color: #ffffff; font-size: 14px;">Stage 2: Hybrid Scoring Engine</strong>
                    <p style="color: #9ca3af; font-size: 13px; margin: 2px 0 0 0;">Combines TF-IDF semantic cosine similarity, proficiency-weighted skills matching, and experience fit scoring.</p>
                </div>
            </div>
            <div style="display: flex; gap: 12px; align-items: flex-start;">
                <span style="background: rgba(6, 182, 212, 0.15); color: #22d3ee; font-weight: 600; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0;">3</span>
                <div>
                    <strong style="color: #ffffff; font-size: 14px;">Stage 3: Behavioral Signal Modifier</strong>
                    <p style="color: #9ca3af; font-size: 13px; margin: 2px 0 0 0;">Adjusts score dynamically using real-time platform engagement (login recency, responsiveness metrics, and notice period constraints).</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Page 2: Dataset Overview
elif page == "Dataset Overview":
    st.markdown("<h1 class='gradient-header'>📊 Dataset Overview</h1>", unsafe_allow_html=True)
    st.markdown("<p class='gradient-subtitle'>Explore demographic structures across the loaded candidate database.</p>", unsafe_allow_html=True)

    st.markdown("<h3 style='color: #ffffff; font-family: Outfit, sans-serif; font-size: 16px; margin-bottom: 12px;'>Profile Demographics Sample</h3>", unsafe_allow_html=True)
    sample_df = pd.DataFrame([{
        "Candidate ID": c["candidate_id"],
        "Name": c["profile"]["anonymized_name"],
        "Title": c["profile"]["current_title"],
        "Location": c["profile"]["location"],
        "Exp (Years)": c["profile"]["years_of_experience"]
    } for c in current_pool[:10]])
    st.table(sample_df)

    st.markdown("<h3 style='color: #ffffff; font-family: Outfit, sans-serif; font-size: 16px; margin-top: 24px; margin-bottom: 12px;'>Behavioral Signals Overview</h3>", unsafe_allow_html=True)
    sample_sig_df = pd.DataFrame([{
        "Candidate ID": c["candidate_id"],
        "Notice (Days)": c["redrob_signals"]["notice_period_days"],
        "Response Rate (%)": int(c["redrob_signals"]["recruiter_response_rate"] * 100),
        "Last Active": c["redrob_signals"]["last_active_date"]
    } for c in current_pool[:10]])
    st.table(sample_sig_df)

# Page 3: JD Analysis
elif page == "JD Analysis":
    st.markdown("<h1 class='gradient-header'>📄 Job Description Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p class='gradient-subtitle'>Examine the target hiring requirements parsed from the released job description document.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='color: #ffffff; font-family: Outfit, sans-serif; font-size: 16px; margin-bottom: 12px;'>Parsed JD Text Snippet</h3>", unsafe_allow_html=True)
        st.text_area("JD Text", jd_text[:2000] + "\n...", height=350)
    with col2:
        st.markdown(f"""
        <div class="glass-panel" style="height: 100%;">
            <h3 style="color: #ffffff; font-family: 'Outfit', sans-serif; margin-top: 0; margin-bottom: 16px; font-size: 16px;">📌 Extracted Requirements & Constraints</h3>
            
            <div class="req-item success-item">
                <span class="req-icon">🎯</span>
                <div>
                    <strong>Target Experience Range</strong>
                    <p>5 - 9 Years required</p>
                </div>
            </div>
            
            <div class="req-item success-item">
                <span class="req-icon">📍</span>
                <div>
                    <strong>Target Office Locations</strong>
                    <p>Noida / Pune, India (Hybrid preferred)</p>
                </div>
            </div>
            
            <div class="req-item success-item">
                <span class="req-icon">⏱️</span>
                <div>
                    <strong>Notice Period Goal</strong>
                    <p>Sub-30 Days</p>
                </div>
            </div>
            
            <div class="req-item danger-item">
                <span class="req-icon">🚫</span>
                <div>
                    <strong>Consulting Firm Exclusion</strong>
                    <p>Excludes TCS, Infosys, Wipro, Accenture, Cognizant, Capgemini, HCL, Tech Mahindra, Mindtree, Mphasis.</p>
                </div>
            </div>
            
            <div class="req-item danger-item">
                <span class="req-icon">🚫</span>
                <div>
                    <strong>Trap Detection</strong>
                    <p>Excludes keyword stuffers, academic-only profiles, and logical contradictions (92 honeypots).</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Page 4: Candidate Ranking
elif page == "Candidate Ranking":
    st.markdown("<h1 class='gradient-header'>🏆 Candidate Ranking - Top 100</h1>", unsafe_allow_html=True)
    st.markdown("<p class='gradient-subtitle'>Top 100 candidates ranked against the job description. Reranking computes in real-time as you adjust weights in the sidebar.</p>", unsafe_allow_html=True)
    
    # Filter search
    search_query = st.text_input("Search candidates by Title or Location:", "")
    
    filtered_pool = current_pool
    if search_query:
        filtered_pool = [c for c in current_pool if search_query.lower() in c["profile"]["current_title"].lower() or search_query.lower() in c["profile"]["location"].lower()]
        
    ranking_data = []
    for idx, c in enumerate(filtered_pool[:100]):
        ranking_data.append({
            "Rank": idx + 1,
            "Candidate ID": c["candidate_id"],
            "Score": c["score"],
            "Name": c["profile"]["anonymized_name"],
            "Current Title": c["profile"]["current_title"],
            "Location": c["profile"]["location"],
            "Notice Period (Days)": c["redrob_signals"]["notice_period_days"],
            "Relocate?": "Yes" if c["redrob_signals"]["willing_to_relocate"] else "No"
        })
        
    if ranking_data:
        st.dataframe(pd.DataFrame(ranking_data), use_container_width=True)
    else:
        st.warning("No candidates matched your search query.")

# Page 5: Candidate Details
elif page == "Candidate Details":
    st.markdown("<h1 class='gradient-header'>👤 Candidate Profile Details</h1>", unsafe_allow_html=True)
    st.markdown("<p class='gradient-subtitle'>Select a candidate ID to view their full credentials, career timeline, and ranking explainability analysis.</p>", unsafe_allow_html=True)
    
    candidate_ids = [c["candidate_id"] for c in current_pool[:100]]
    selected_id = st.selectbox("Select Candidate ID:", candidate_ids)
    
    candidate = next(c for c in current_pool if c["candidate_id"] == selected_id)
    
    st.markdown('<div style="border-top: 1px solid rgba(255,255,255,0.08); margin: 20px 0;"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""
        <div class="glass-panel">
            <h2 style="color: #ffffff; font-family: 'Outfit', sans-serif; margin-top: 0; font-size: 22px; margin-bottom: 4px;">{candidate['profile']['anonymized_name']}</h2>
            <h4 style="color: #a5b4fc; font-family: 'Inter', sans-serif; margin-top: 0; font-weight: 500; font-size: 15px; margin-bottom: 8px;">{candidate['profile']['current_title']}</h4>
            <p style="color: #9ca3af; font-size: 13px; margin-bottom: 16px;">
                📍 {candidate['profile']['location']}, {candidate['profile']['country']} &nbsp;|&nbsp; 💼 {candidate['profile']['years_of_experience']} Years of Experience
            </p>
            <div style="background: rgba(99, 102, 241, 0.05); border-left: 3px solid #6366F1; padding: 12px 16px; border-radius: 8px; color: #e5e7eb; font-size: 14px; line-height: 1.5;">
                <strong>Summary:</strong> {candidate['profile']['summary']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='color: #ffffff; font-family: Outfit, sans-serif; margin-top: 24px; font-size: 18px; margin-bottom: 12px;'>💼 Career History</h3>", unsafe_allow_html=True)
        for ch in candidate["career_history"]:
            st.markdown(f"""
            <div class='glass-panel' style='padding: 16px !important; margin-bottom: 12px !important;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <strong style='color: #ffffff; font-size: 15px;'>{ch['title']} at {ch['company']}</strong>
                    <span style='color: #8B5CF6; font-size: 12px; font-weight: 600; background: rgba(139, 92, 246, 0.1); padding: 4px 8px; border-radius: 6px;'>{ch['start_date']} - {ch['end_date'] or 'Present'}</span>
                </div>
                <p style='color: #9ca3af; font-size: 12px; margin: 4px 0 10px 0;'>Duration: {ch['duration_months']} months | Industry: {ch['industry']}</p>
                <div style='color: #d1d5db; font-size: 13px; line-height: 1.5;'>{ch['description']}</div>
            </div>
            """, unsafe_allow_html=True)
            
    with col2:
        ee = ExplainabilityEngine()
        explanation = ee.generate_explanation(candidate)
        
        skills_html = "".join([f"<div style='margin-bottom: 6px; font-size: 13px; color: #10B981;'>✓ {sk}</div>" for sk in explanation["matched_skills"]]) if explanation["matched_skills"] else "<div style='color: #9ca3af; font-size: 13px;'>None detected</div>"
        strengths_html = "".join([f"<div style='margin-bottom: 6px; font-size: 13px; color: #6366F1;'>✓ {st_point}</div>" for st_point in explanation["strengths"]]) if explanation["strengths"] else "<div style='color: #9ca3af; font-size: 13px;'>None detected</div>"
        
        concerns_html = ""
        if explanation["concerns"]:
            concerns_html = "".join([f"<div style='margin-bottom: 6px; font-size: 13px; color: #EF4444;'>⚠ {con_point}</div>" for con_point in explanation["concerns"]])
        else:
            concerns_html = "<div style='color: #10B981; font-size: 13px;'>No major concerns detected.</div>"
            
        st.markdown(f"""
        <div class="glass-panel" style="margin-bottom: 16px !important;">
            <h3 style="color: #ffffff; font-family: 'Outfit', sans-serif; font-size: 15px; margin-top: 0; margin-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 8px;">🧠 AI Explainability</h3>
            
            <strong style="color: #a5b4fc; font-size: 11px; text-transform: uppercase; letter-spacing: 0.03em;">Matched Skills</strong>
            <div style="margin: 8px 0 16px 0;">{skills_html}</div>
            
            <strong style="color: #a5b4fc; font-size: 11px; text-transform: uppercase; letter-spacing: 0.03em;">Core Strengths</strong>
            <div style="margin: 8px 0 16px 0;">{strengths_html}</div>
            
            <strong style="color: #fca5a5; font-size: 11px; text-transform: uppercase; letter-spacing: 0.03em;">Areas of Concern</strong>
            <div style="margin: 8px 0 0 0;">{concerns_html}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="glass-panel">
            <h3 style="color: #ffffff; font-family: 'Outfit', sans-serif; font-size: 15px; margin-top: 0; margin-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 8px;">📶 Platform Engagement</h3>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px;">
                <span style="color: #9ca3af;">Last Active:</span>
                <span style="color: #ffffff; font-weight: 500;">{candidate['redrob_signals']['last_active_date']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px;">
                <span style="color: #9ca3af;">Response Rate:</span>
                <span style="color: #06B6D4; font-weight: 600;">{int(candidate['redrob_signals']['recruiter_response_rate'] * 100)}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px;">
                <span style="color: #9ca3af;">Avg Response Time:</span>
                <span style="color: #ffffff; font-weight: 500;">{candidate['redrob_signals']['avg_response_time_hours']} hrs</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 13px;">
                <span style="color: #9ca3af;">Interview Completion:</span>
                <span style="color: #10B981; font-weight: 600;">{int(candidate['redrob_signals']['interview_completion_rate'] * 100)}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Page 6: Analytics
elif page == "Analytics":
    st.markdown("<h1 class='gradient-header'>📈 Ranking Analytics</h1>", unsafe_allow_html=True)
    st.markdown("<p class='gradient-subtitle'>Visualize scores and metric distributions for the Top 100 candidates.</p>", unsafe_allow_html=True)
    
    top_100 = current_pool[:100]
    
    # Configure dark background style for matplotlib plots
    plt.style.use("dark_background")
    
    st.markdown("<h3 style='color: #ffffff; font-family: Outfit, sans-serif; font-size: 16px; margin-bottom: 12px;'>Similarity Scores vs Skills Score</h3>", unsafe_allow_html=True)
    plot_data = pd.DataFrame([{
        "Candidate": c["candidate_id"],
        "Semantic Score": c["features"]["sim_profile"] * 0.6 + c["features"]["sim_history"] * 0.4,
        "Skills Score": min(1.0, c["features"]["skills_required_score"] / 5.0)
    } for c in top_100])
    
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    sns.scatterplot(data=plot_data, x="Semantic Score", y="Skills Score", ax=ax, color="#8B5CF6", s=120, edgecolor="#06B6D4", alpha=0.8)
    ax.set_title("Semantic Match vs Technical Capability", fontsize=12, pad=15, color="#ffffff")
    ax.set_xlabel("Semantic Score", color="#a5b4fc", fontsize=10)
    ax.set_ylabel("Skills Score", color="#a5b4fc", fontsize=10)
    ax.spines['bottom'].set_color('rgba(255, 255, 255, 0.1)')
    ax.spines['left'].set_color('rgba(255, 255, 255, 0.1)')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#9ca3af')
    st.pyplot(fig)

    st.markdown("<h3 style='color: #ffffff; font-family: Outfit, sans-serif; font-size: 16px; margin-top: 24px; margin-bottom: 12px;'>Experience Distribution (Top 100)</h3>", unsafe_allow_html=True)
    exp_data = [c["profile"]["years_of_experience"] for c in top_100]
    
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    fig2.patch.set_facecolor('none')
    ax2.set_facecolor('none')
    sns.histplot(exp_data, kde=True, bins=10, ax=ax2, color="#06B6D4", edgecolor="none", alpha=0.7)
    ax2.set_title("Distribution of Years of Experience", fontsize=12, pad=15, color="#ffffff")
    ax2.set_xlabel("Years of Experience", color="#a5b4fc", fontsize=10)
    ax2.set_ylabel("Count", color="#a5b4fc", fontsize=10)
    ax2.spines['bottom'].set_color('rgba(255, 255, 255, 0.1)')
    ax2.spines['left'].set_color('rgba(255, 255, 255, 0.1)')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.tick_params(colors='#9ca3af')
    st.pyplot(fig2)

# Page 7: Submission Export
elif page == "Submission Export":
    st.markdown("<h1 class='gradient-header'>📤 Export Submission CSV</h1>", unsafe_allow_html=True)
    st.markdown("<p class='gradient-subtitle'>Generate and download the formatted CSV file matching the hackathon validator specifications.</p>", unsafe_allow_html=True)
    
    participant_id = st.text_input("Enter Participant Team ID:", "team_talentrank")
    
    if st.button("Compile Submission CSV"):
        st.info("Compiling and running pre-validation check...")
        
        output_csv = config.OUTPUTS_DIR / f"{participant_id}.csv"
        config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        
        engine = ExplainabilityEngine()
        
        with open(output_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["candidate_id", "rank", "score", "reasoning"])
            for idx, c in enumerate(current_pool[:100]):
                rank = idx + 1
                reasoning = engine.generate_explanation_text(c, rank)
                writer.writerow([c["candidate_id"], rank, c["score"], reasoning])
                
        # Import validator directly to verify
        sys.path.append(str(config.DATA_DIR))
        from validate_submission import validate_submission
        errors = validate_submission(str(output_csv))
        
        if errors:
            st.error("Validation FAILED with the following issues:")
            for err in errors:
                st.error(f"- {err}")
        else:
            st.success("Validation PASSED! The submission CSV is fully compliant.")
            
            # Read file to enable download button
            with open(output_csv, "r", encoding="utf-8") as f:
                csv_data = f.read()
                
            st.download_button(
                label="Download Submission CSV",
                data=csv_data,
                file_name=f"{participant_id}.csv",
                mime="text/csv"
            )

