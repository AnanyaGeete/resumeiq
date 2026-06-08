import streamlit as st
from analyser import analyse_resume
from parser import extract_text

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ — AI Resume Analyser",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PINK THEME CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── BASE ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #fff0f5 !important;
}
h1,h2,h3 { font-family: 'Playfair Display', serif !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #ff6fa8 0%, #ff3d7f 100%) !important;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.25) !important;
    border: 1.5px solid rgba(255,255,255,0.5) !important;
    color: white !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] textarea {
    background: rgba(255,255,255,0.2) !important;
    border: 1.5px solid rgba(255,255,255,0.4) !important;
    color: white !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] label { color: white !important; font-weight: 500 !important; }
[data-testid="stSidebar"] a { color: #ffe0ef !important; }

/* ── HEADER ── */
.hero {
    background: linear-gradient(135deg, #ff3d7f 0%, #ff6fa8 50%, #ffb3d1 100%);
    padding: 2.5rem 2.5rem 2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(255,61,127,0.25);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '💗';
    position: absolute;
    font-size: 120px;
    right: 40px; top: -10px;
    opacity: 0.15;
}
.hero h1 { color: white !important; font-size: 3rem; margin: 0; letter-spacing: -1px; }
.hero p  { color: rgba(255,255,255,0.85); margin: 0.5rem 0 0; font-size: 1.1rem; }

/* ── CARDS ── */
.card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 2px 16px rgba(255,61,127,0.1);
    border: 1px solid #ffd6e7;
    margin-bottom: 1rem;
}

/* ── SCORE BOXES ── */
.score-box {
    background: white;
    border: 2px solid #ffb3d1;
    border-radius: 16px;
    padding: 1.2rem 0.8rem;
    text-align: center;
    box-shadow: 0 4px 12px rgba(255,61,127,0.1);
    transition: transform 0.2s;
}
.score-box:hover { transform: translateY(-3px); }
.score-num   { font-family: 'Playfair Display', serif; font-size: 2.6rem; font-weight: 800; }
.score-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #ff6fa8; font-weight: 600; margin-bottom: 6px; }
.badge-great { background:#ffe0ef; color:#d6005a; padding:3px 12px; border-radius:100px; font-size:12px; font-weight:600; display:inline-block; margin-top:6px; }
.badge-good  { background:#fff3e0; color:#e65100; padding:3px 12px; border-radius:100px; font-size:12px; font-weight:600; display:inline-block; margin-top:6px; }
.badge-poor  { background:#fce4ec; color:#c62828; padding:3px 12px; border-radius:100px; font-size:12px; font-weight:600; display:inline-block; margin-top:6px; }

/* ── LIST ITEMS ── */
.strength-item {
    background: linear-gradient(90deg, #fff0f5, #fff8fb);
    border-left: 4px solid #ff3d7f;
    padding: 0.85rem 1rem;
    border-radius: 0 12px 12px 0;
    margin-bottom: 0.6rem;
    font-size: 0.95rem;
    color: #3a1a2a;
}
.improve-item {
    background: linear-gradient(90deg, #fff8e1, #fffdf0);
    border-left: 4px solid #ffb300;
    padding: 0.85rem 1rem;
    border-radius: 0 12px 12px 0;
    margin-bottom: 0.6rem;
    font-size: 0.95rem;
    color: #3a2a00;
}

/* ── KEYWORD CHIPS ── */
.kw-found   { background:#ffe0ef; color:#c2185b; padding:5px 14px; border-radius:100px; font-size:13px; font-weight:500; display:inline-block; margin:4px; border: 1px solid #ffb3d1; }
.kw-missing { background:#fce4ec; color:#b71c1c; padding:5px 14px; border-radius:100px; font-size:13px; font-weight:500; display:inline-block; margin:4px; border: 1px solid #ffcdd2; }

/* ── REWRITE BOX ── */
.rewrite-box {
    background: linear-gradient(135deg, #fff0f5, #fff8fb);
    border: 2px solid #ffb3d1;
    border-radius: 14px;
    padding: 1.5rem;
    font-size: 1rem;
    line-height: 1.8;
    color: #3a1a2a;
    font-style: italic;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 100px !important;
    padding: 6px 18px !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: #ff3d7f !important;
    color: white !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #ff3d7f, #ff6fa8) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.6rem 2rem !important;
    box-shadow: 0 4px 15px rgba(255,61,127,0.35) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255,61,127,0.45) !important;
}

/* ── PROGRESS BAR ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #ff3d7f, #ff6fa8) !important;
    border-radius: 100px !important;
}

/* ── ALERTS ── */
.stSuccess { border-left-color: #ff3d7f !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    border: 2px dashed #ffb3d1 !important;
    border-radius: 16px !important;
    background: white !important;
    padding: 1rem !important;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── HERO HEADER ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>Resume<span style="color:#ffe0ef">IQ</span> 💗</h1>
    <p>AI-powered resume analysis · Instant ATS feedback · 100% Free</p>
</div>
""", unsafe_allow_html=True)

# ── AUTO LOAD API KEY FROM SECRETS ──────────────────────────────────────────
try:
    api_key = st.secrets["GROQ_API_KEY"]
    key_from_secret = True
except:
    api_key = None
    key_from_secret = False

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ ResumeIQ")

    if not key_from_secret:
        st.markdown("**API Key Required**")
        st.markdown("[🔑 Get Free Groq Key](https://console.groq.com/keys)")
        st.divider()
        api_key = st.text_input(
            "Paste your Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Free at console.groq.com/keys"
        )
        st.divider()
    else:
        st.success("✓ App ready to use!")
        st.divider()

    st.markdown("**Job Description (optional)**")
    job_desc = st.text_area(
        "Job Description",
        placeholder="Paste the job listing here to get a match score...",
        height=180
    )

    st.divider()
    st.markdown("""
    **What you get:**
    - 💗 Overall score
    - 📋 ATS compatibility
    - ⚡ Impact rating
    - ✨ Clarity score
    - 🎯 Job match (if JD provided)
    - 🔑 Keyword analysis
    - ✍️ AI rewritten summary
    """)

# ── UPLOAD SECTION ────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.markdown("### 📄 Upload Your Resume")
    uploaded_file = st.file_uploader(
        "Supports PDF and TXT files (max 10MB)",
        type=["pdf", "txt"],
        help="Your file is never stored — processed only during this session"
    )
    if uploaded_file:
        st.success(f"✓ **{uploaded_file.name}** ready ({uploaded_file.size // 1024} KB)")

with col2:
    st.markdown("### 🚀 Run Analysis")
    st.markdown("Make sure you've added your API key and uploaded a resume.")

    if not api_key:
        st.warning("⬅️ Add your Groq API key in the sidebar")
    elif not uploaded_file:
        st.info("⬅️ Upload your resume on the left")
    else:
        st.success("✓ Ready to analyse!")

    analyse_clicked = st.button(
        "💗 Analyse My Resume",
        use_container_width=True,
        disabled=(not uploaded_file or not api_key)
    )

# ── RUN ANALYSIS ──────────────────────────────────────────────────────────────
if analyse_clicked and uploaded_file and api_key:

    with st.spinner("📖 Reading your resume..."):
        try:
            resume_text = extract_text(uploaded_file)
            if not resume_text.strip():
                st.error("Could not read text from this file. Try a plain text PDF.")
                st.stop()
        except Exception as e:
            st.error(f"File error: {e}")
            st.stop()

    with st.spinner("🤖 Analysing with Llama AI (via Groq)..."):
        try:
            result = analyse_resume(resume_text, job_desc, api_key)
        except Exception as e:
            st.error(f"AI Error: {e}")
            st.stop()

    st.session_state["result"] = result
    st.session_state["filename"] = uploaded_file.name

# ── SHOW RESULTS ──────────────────────────────────────────────────────────────
if "result" in st.session_state:
    result   = st.session_state["result"]
    scores   = result.get("scores", {})
    filename = st.session_state.get("filename", "resume")

    st.divider()
    st.markdown("## 💗 Your Analysis Results")

    # ── SCORE CARDS ──
    score_labels = {"overall":"Overall","ats":"ATS Score","impact":"Impact","clarity":"Clarity","jobMatch":"Job Match"}
    score_colors = {"overall":"#ff3d7f","ats":"#e91e8c","impact":"#ff6fa8","clarity":"#f06292","jobMatch":"#ad1457"}

    cols = st.columns(len(scores))
    for i, (key, val) in enumerate(scores.items()):
        color = score_colors.get(key, "#ff3d7f")
        badge_class = "badge-great" if val >= 75 else "badge-good" if val >= 50 else "badge-poor"
        badge_text  = "Great ✨" if val >= 75 else "Good 👍" if val >= 50 else "Needs Work 💪"
        with cols[i]:
            st.markdown(f"""
            <div class="score-box">
                <div class="score-label">{score_labels.get(key, key)}</div>
                <div class="score-num" style="color:{color}">{val}</div>
                <div class="{badge_class}">{badge_text}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── PROGRESS BARS ──
    with st.expander("📊 Score Breakdown", expanded=True):
        for key, val in scores.items():
            st.markdown(f"**{score_labels.get(key, key)}** — {val}/100")
            st.progress(val / 100)

    st.divider()

    # ── TABS ──
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Summary", "💪 Strengths", "🔧 Improvements", "🏷️ Keywords", "✨ AI Rewrite"
    ])

    with tab1:
        st.markdown("### Overall Summary")
        st.markdown(f"""<div class="card">{result.get("summary", "")}</div>""", unsafe_allow_html=True)

    with tab2:
        st.markdown("### What's Working For You")
        for item in result.get("strengths", []):
            st.markdown(f'<div class="strength-item">💗 {item}</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown("### Areas To Improve")
        for item in result.get("improvements", []):
            st.markdown(f'<div class="improve-item">→ {item}</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown("### Keyword Analysis")
        cola, colb = st.columns(2)
        with cola:
            st.markdown("**✅ Found in your resume**")
            html = " ".join([f'<span class="kw-found">{k}</span>' for k in result.get("keywordsFound", [])])
            st.markdown(html or "None detected", unsafe_allow_html=True)
        with colb:
            st.markdown("**❌ Missing — add these**")
            html = " ".join([f'<span class="kw-missing">{k}</span>' for k in result.get("keywordsMissing", [])])
            st.markdown(html or "None detected", unsafe_allow_html=True)

    with tab5:
        st.markdown("### AI-Rewritten Professional Summary")
        st.markdown("> Copy this and replace your current summary. It's optimised for ATS and recruiters.")
        st.markdown(f'<div class="rewrite-box">{result.get("rewrittenSummary", "")}</div>', unsafe_allow_html=True)
        st.code(result.get("rewrittenSummary", ""), language=None)

    st.divider()

    # ── DOWNLOAD ──
    score_labels_full = {"overall":"Overall","ats":"ATS Score","impact":"Impact","clarity":"Clarity","jobMatch":"Job Match"}
    report = "\n".join([
        "ResumeIQ — AI Resume Analysis Report",
        "=" * 40,
        f"File: {filename}",
        "",
        "SCORES",
        *[f"{score_labels_full.get(k,k)}: {v}/100" for k,v in scores.items()],
        "",
        "SUMMARY",
        result.get("summary",""),
        "",
        "STRENGTHS",
        *[f"• {s}" for s in result.get("strengths",[])],
        "",
        "IMPROVEMENTS",
        *[f"• {s}" for s in result.get("improvements",[])],
        "",
        "KEYWORDS FOUND", ", ".join(result.get("keywordsFound",[])),
        "",
        "KEYWORDS MISSING", ", ".join(result.get("keywordsMissing",[])),
        "",
        "AI REWRITTEN SUMMARY",
        result.get("rewrittenSummary","")
    ])

    st.download_button(
        "⬇️ Download Full Report",
        data=report,
        file_name="ResumeIQ_Report.txt",
        mime="text/plain",
        use_container_width=True
    )
