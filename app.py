"""Streamlit web application for Semantic Resume Ranker (Blue & White Theme)."""

import altair as alt
import pandas as pd
import streamlit as st

from src.embedder import get_embedder
from src.ranker import rank_resumes
from src.report import generate_csv_report, generate_json_report, results_to_dataframe
from src.scorer import WEIGHTS
from src.skill_extractor import get_skill_extractor

# Configure page metadata and layout
st.set_page_config(
    page_title="Semantic Resume Ranker",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Blue & White crisp UI with deep black text
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0F172A;
    }

    /* Main container background */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Hero Header Banner (Deep Royal Blue Gradient) */
    .hero-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 55%, #3B82F6 100%);
        padding: 30px 36px;
        border-radius: 16px;
        color: #FFFFFF;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.28), 0 8px 10px -6px rgba(37, 99, 235, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.025em;
        color: #FFFFFF;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #DBEAFE;
        margin-top: 6px;
        margin-bottom: 0;
        font-weight: 500;
    }

    /* Pill Badges for Skills */
    .badge-pill {
        display: inline-block;
        padding: 5px 13px;
        margin: 3px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        transition: all 0.15s ease-in-out;
    }
    .badge-pill:hover {
        transform: translateY(-1px) scale(1.04);
    }
    .badge-green {
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #6EE7B7;
        box-shadow: 0 1px 3px rgba(6, 95, 70, 0.06);
    }
    .badge-red {
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FCA5A5;
        box-shadow: 0 1px 3px rgba(153, 27, 27, 0.06);
    }
    .badge-blue {
        background-color: #EFF6FF;
        color: #1E40AF;
        border: 1px solid #93C5FD;
        box-shadow: 0 1px 3px rgba(30, 64, 175, 0.06);
    }
    .badge-grey {
        background-color: #F8FAFC;
        color: #334155;
        border: 1px solid #CBD5E1;
    }

    /* Modern Metric Cards (Pure White with Royal Blue Top Border) */
    .metric-card {
        background: #FFFFFF;
        padding: 20px 18px;
        border-radius: 14px;
        border: 1px solid #DBEAFE;
        border-top: 4px solid #2563EB;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.07);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 24px rgba(37, 99, 235, 0.15);
        border-color: #BFDBFE;
    }
    .metric-card h4 {
        margin: 0;
        font-size: 0.85rem;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 700;
    }
    .metric-card .metric-val {
        font-size: 2rem;
        font-weight: 800;
        color: #0F172A;
        margin: 6px 0 0 0;
        letter-spacing: -0.02em;
    }
    .metric-card .metric-sub {
        font-size: 0.83rem;
        color: #334155;
        margin-top: 4px;
        font-weight: 500;
    }

    /* Status Tier Badges */
    .tier-tag {
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 8px;
        margin-left: 8px;
        vertical-align: middle;
        letter-spacing: 0.02em;
    }
    .tier-elite {
        background: #ECFDF5;
        color: #047857;
        border: 1px solid #A7F3D0;
    }
    .tier-strong {
        background: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
    }
    .tier-moderate {
        background: #FFFBEB;
        color: #B45309;
        border: 1px solid #FDE68A;
    }
    .tier-low {
        background: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FECACA;
    }

    /* Disclaimer and Info Boxes */
    .disclaimer-box {
        background: #EFF6FF;
        border-left: 4px solid #2563EB;
        padding: 14px 18px;
        border-radius: 8px;
        font-size: 0.9rem;
        color: #1E293B;
        margin-bottom: 22px;
        border: 1px solid #DBEAFE;
        border-left-width: 4px;
        line-height: 1.5;
    }

    /* Primary Buttons Styling */
    .stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: #FFFFFF !important;
        font-weight: 700;
        border-radius: 10px;
        border: none;
        padding: 8px 18px;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
        transition: all 0.15s ease-in-out;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%);
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35);
        transform: translateY(-1px);
        color: #FFFFFF !important;
    }

    /* Download Buttons Styling */
    .stDownloadButton > button {
        background: #FFFFFF !important;
        color: #1E40AF !important;
        border: 1.5px solid #BFDBFE !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        transition: all 0.15s ease-in-out !important;
    }
    .stDownloadButton > button:hover {
        background: #EFF6FF !important;
        border-color: #2563EB !important;
        color: #1D4ED8 !important;
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_cached_nlp_models():
    """Cache models in Streamlit session to prevent reload on re-renders."""
    try:
        import spacy
        spacy.load("en_core_web_sm")
    except OSError:
        try:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        except Exception:
            pass

    embedder = get_embedder()
    skill_extractor = get_skill_extractor()
    return embedder, skill_extractor


def render_skill_badges(skills, badge_type):
    """Render list of skills as styled HTML pill badges."""
    if not skills:
        return "<span style='color: #64748B; font-style: italic; font-weight: 500;'>None detected</span>"
    pills = "".join(
        f"<span class='badge-pill badge-{badge_type}'>{skill}</span>"
        for skill in skills
    )
    return pills


def get_tier_badge(score: float) -> str:
    """Return colored tier badge based on candidate score."""
    if score >= 80:
        return "<span class='tier-tag tier-elite'>🌟 Elite Fit</span>"
    elif score >= 65:
        return "<span class='tier-tag tier-strong'>✨ Strong Fit</span>"
    elif score >= 50:
        return "<span class='tier-tag tier-moderate'>⚡ Moderate Fit</span>"
    return "<span class='tier-tag tier-low'>🔻 Low Fit</span>"


def render_head_to_head(res_a, res_b):
    """Render interactive head-to-head comparison between two candidates."""
    st.markdown("### ⚔️ Head-to-Head Comparison")
    c1, c2 = st.columns(2)

    badge_a = get_tier_badge(res_a.final_score)
    badge_b = get_tier_badge(res_b.final_score)

    with c1:
        st.markdown(f"#### 🅰️ {res_a.filename}")
        st.markdown(f"**Final Score:** `{res_a.final_score:.1f}/100` {badge_a}", unsafe_allow_html=True)
    with c2:
        st.markdown(f"#### 🅱️ {res_b.filename}")
        st.markdown(f"**Final Score:** `{res_b.final_score:.1f}/100` {badge_b}", unsafe_allow_html=True)

    delta_score = res_a.final_score - res_b.final_score
    delta_str = f"+{delta_score:.1f}" if delta_score > 0 else f"{delta_score:.1f}"
    winner = res_a.filename if delta_score > 0 else (res_b.filename if delta_score < 0 else "Tie")

    st.info(f"🏆 **Margin Difference:** `{delta_str}` points in favor of **{winner}**")

    # Metrics comparison table
    skill_a_str = f"{res_a.skill_score:.1f}%" if res_a.skill_score is not None else "N/A"
    skill_b_str = f"{res_b.skill_score:.1f}%" if res_b.skill_score is not None else "N/A"
    comparison_df = pd.DataFrame(
        {
            "Evaluation Metric": [
                "Final Score",
                "Semantic Similarity",
                "Skill Match",
                "Experience Relevance",
                "Lexical Overlap",
                "Matched Skills Count",
            ],
            f"🅰️ {res_a.filename}": [
                f"{res_a.final_score:.1f}/100",
                f"{res_a.semantic_score:.1f}/100",
                skill_a_str,
                f"{res_a.experience_section_score:.1f}/100",
                f"{res_a.lexical_score:.1f}/100",
                str(len(res_a.matched_skills)),
            ],
            f"🅱️ {res_b.filename}": [
                f"{res_b.final_score:.1f}/100",
                f"{res_b.semantic_score:.1f}/100",
                skill_b_str,
                f"{res_b.experience_section_score:.1f}/100",
                f"{res_b.lexical_score:.1f}/100",
                str(len(res_b.matched_skills)),
            ],
        }
    )
    st.dataframe(comparison_df.set_index("Evaluation Metric"), use_container_width=True)

    # Venn-like Skill Overlap
    set_a = set(res_a.matched_skills)
    set_b = set(res_b.matched_skills)
    shared_skills = sorted(list(set_a.intersection(set_b)))
    only_a = sorted(list(set_a - set_b))
    only_b = sorted(list(set_b - set_a))

    v1, v2, v3 = st.columns(3)
    with v1:
        st.markdown(f"**Unique to 🅰️ ({len(only_a)}):**")
        st.markdown(render_skill_badges(only_a, "blue"), unsafe_allow_html=True)
    with v2:
        st.markdown(f"**Shared Skills ({len(shared_skills)}):**")
        st.markdown(render_skill_badges(shared_skills, "green"), unsafe_allow_html=True)
    with v3:
        st.markdown(f"**Unique to 🅱️ ({len(only_b)}):**")
        st.markdown(render_skill_badges(only_b, "red"), unsafe_allow_html=True)


def main():
    """Main application routine."""
    st.markdown(
        """
        <div class='hero-header'>
            <h1 class='hero-title'>📄 Semantic Resume Ranker</h1>
            <p class='hero-subtitle'>
                Explainable, multi-factor NLP screening with dense embeddings,
                taxonomy phrase matching & smart analytics.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='disclaimer-box'>
            🛡️ <strong>Assistive Screening Intelligence:</strong> Algorithmic scores and skill matches provide
            an objective baseline for candidate triage. Designed to assist human hiring teams with explainable AI.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar inputs
    st.sidebar.header("🎯 Job Description")

    # Sample JD presets
    sample_backend_jd = (
        "We are seeking a Senior Full-Stack Python Engineer.\n\n"
        "Requirements:\n"
        "- 4+ years building scalable backends with Python, FastAPI, and Django.\n"
        "- Strong relational database expertise with PostgreSQL and Redis caching.\n"
        "- Production experience with Docker, Kubernetes, and CI/CD pipelines on AWS.\n"
        "- Machine Learning knowledge (PyTorch, Scikit-Learn) and REST API design.\n"
        "- Frontend experience with React and TypeScript is a plus.\n"
        "- Excellent communication, leadership, and agile collaboration."
    )
    sample_data_jd = (
        "We are looking for a Senior Data Scientist / ML Engineer.\n\n"
        "Requirements:\n"
        "- 3+ years in Python, PyTorch, TensorFlow, and Scikit-Learn.\n"
        "- Experience with NLP transformer models, embeddings, and vector databases.\n"
        "- Solid SQL, PostgreSQL, and BigQuery data pipeline experience.\n"
        "- Production deployment with Docker, FastAPI, and GCP/AWS.\n"
        "- Strong background in statistics, data cleaning, and experimentation."
    )

    if "jd_text_value" not in st.session_state:
        st.session_state["jd_text_value"] = sample_backend_jd

    jd_mode = st.sidebar.radio("JD Input Format", ["Paste Text", "Upload File"], index=0)

    jd_content = ""
    jd_filename = "job_description.txt"

    if jd_mode == "Paste Text":
        preset_cols = st.sidebar.columns(2)
        if preset_cols[0].button("🐍 Backend JD", use_container_width=True):
            st.session_state["jd_text_value"] = sample_backend_jd
            st.rerun()
        if preset_cols[1].button("📊 ML Data JD", use_container_width=True):
            st.session_state["jd_text_value"] = sample_data_jd
            st.rerun()

        jd_content = st.sidebar.text_area(
            "Job Description Text:",
            value=st.session_state["jd_text_value"],
            height=200,
        )
    else:
        uploaded_jd = st.sidebar.file_uploader(
            "Upload JD Document", type=["pdf", "docx"], key="jd_upload"
        )
        if uploaded_jd is not None:
            jd_content = uploaded_jd.read()
            jd_filename = uploaded_jd.name

    st.sidebar.markdown("---")
    st.sidebar.header("📑 Candidate Resumes")
    uploaded_resumes = st.sidebar.file_uploader(
        "Upload Resumes (.pdf, .docx)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help="Upload one or more candidate resumes to rank.",
    )

    # Expandable Scoring Weights
    with st.sidebar.expander("⚙️ Scoring Weights Customization", expanded=False):
        st.write("Tune scoring factor weights (automatically normalized to 100%):")
        w_semantic = st.slider("Semantic Similarity", 0.0, 1.0, WEIGHTS["semantic_score"], 0.05)
        w_skill = st.slider("Skill Match Ratio", 0.0, 1.0, WEIGHTS["skill_score"], 0.05)
        w_exp = st.slider("Experience Relevance", 0.0, 1.0, WEIGHTS["experience_section_score"], 0.05)
        w_lex = st.slider("Lexical (TF-IDF)", 0.0, 1.0, WEIGHTS["lexical_score"], 0.05)

        total_weight = w_semantic + w_skill + w_exp + w_lex
        if total_weight > 0:
            st.caption(
                f"Effective: Semantic: {w_semantic/total_weight:.0%} | "
                f"Skill: {w_skill/total_weight:.0%} | "
                f"Exp: {w_exp/total_weight:.0%} | "
                f"Lex: {w_lex/total_weight:.0%}"
            )
        else:
            st.error("At least one weight must be greater than zero.")

    custom_weights = {
        "semantic_score": w_semantic,
        "skill_score": w_skill,
        "experience_section_score": w_exp,
        "lexical_score": w_lex,
    }

    # Load NLP Models with spinner
    with st.spinner("Initializing embeddings and skill taxonomy models..."):
        embedder, skill_extractor = load_cached_nlp_models()

    if not jd_content:
        st.info("👈 Please provide a Job Description in the sidebar to get started.")
        return

    # Check if demo resumes should be used when no files are uploaded
    run_demo = False
    if not uploaded_resumes:
        st.markdown("### 💡 Quick Try: Run Sample Benchmark")
        st.write("No resumes uploaded yet. Click below to evaluate two pre-configured candidate profiles:")
        if st.button("🚀 Run Demo Comparison (Strong vs. Weak Match)"):
            run_demo = True

    resume_payloads = []
    if uploaded_resumes:
        for f in uploaded_resumes:
            resume_payloads.append((f.name, f.read()))
    elif run_demo:
        strong_resume = (
            "Alex Morgan\n"
            "Summary: Senior Full-Stack Python Engineer with 6 years of expertise building resilient backends.\n"
            "Technical Skills: Python, FastAPI, Django, PostgreSQL, Redis, Docker, Kubernetes, AWS, CI/CD, React, "
            "TypeScript, PyTorch, REST API\n"
            "Work Experience: Senior Software Engineer at FinTech Corp.\n"
            "- Architected microservices with FastAPI and PostgreSQL handling 50k requests per minute.\n"
            "- Deployed Docker containers via Kubernetes and GitHub Actions CI/CD on AWS.\n"
            "- Integrated PyTorch ML models to automate financial forecasting, saving 30% calculation time.\n"
            "Education: B.S. in Computer Science"
        )
        weak_resume = (
            "Sam Taylor\n"
            "Summary: Junior Marketing Coordinator with graphic design experience.\n"
            "Skills: Photoshop, Figma, Social Media Marketing, Content Writing, Microsoft Word, Communication\n"
            "Work Experience: Marketing Associate at Retail Brand.\n"
            "- Designed social media graphics and brochures.\n"
            "- Managed promotional events and email campaigns.\n"
            "Education: B.A. in Communications"
        )
        resume_payloads = [
            ("Alex_Morgan_Senior_Python_Dev.txt", strong_resume),
            ("Sam_Taylor_Marketing_Associate.txt", weak_resume),
        ]

    if not resume_payloads:
        return

    # Execute ranking
    with st.spinner("Processing documents, parsing sections, and computing semantic embeddings..."):
        results, errors = rank_resumes(
            jd_input=jd_content,
            resumes=resume_payloads,
            jd_filename=jd_filename,
            custom_weights=custom_weights,
            embedder=embedder,
            skill_extractor=skill_extractor,
        )

    if errors:
        for err in errors:
            st.error(f"⚠️ Failed to process file **{err['filename']}**: {err['error']}")

    if not results:
        st.warning("No valid resumes could be scored.")
        return

    # Key Performance Indicators row
    top_candidate = results[0]
    avg_score = sum(r.final_score for r in results) / len(results)
    avg_skill_pct = (
        sum(r.skill_score for r in results if r.skill_score is not None)
        / max(1, len([r for r in results if r.skill_score is not None]))
    )

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(
            f"<div class='metric-card'>"
            f"<h4>🏆 Top Candidate</h4>"
            f"<div class='metric-val'>{top_candidate.final_score:.1f}"
            f"<span style='font-size: 1.1rem; color: #2563EB;'>/100</span></div>"
            f"<div class='metric-sub' style='overflow: hidden; text-overflow: ellipsis; white-space: nowrap;'>"
            f"{top_candidate.filename}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with kpi2:
        st.markdown(
            f"<div class='metric-card'>"
            f"<h4>📊 Cohort Average</h4>"
            f"<div class='metric-val'>{avg_score:.1f}"
            f"<span style='font-size: 1.1rem; color: #2563EB;'>/100</span></div>"
            f"<div class='metric-sub'>Overall Mean Score</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with kpi3:
        st.markdown(
            f"<div class='metric-card'>"
            f"<h4>🎯 Avg Skill Match</h4>"
            f"<div class='metric-val'>{avg_skill_pct:.1f}"
            f"<span style='font-size: 1.1rem; color: #2563EB;'>%</span></div>"
            f"<div class='metric-sub'>JD Coverage Ratio</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with kpi4:
        st.markdown(
            f"<div class='metric-card'>"
            f"<h4>📑 Candidates</h4>"
            f"<div class='metric-val'>{len(results)}</div>"
            f"<div class='metric-sub'>Total Evaluated</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Interactive Navigation Tabs
    tab_leaderboard, tab_deepdive, tab_head2head, tab_jd = st.tabs(
        [
            "🏆 Leaderboard & Analytics",
            "🔍 Candidate Deep Dive",
            "⚔️ Head-to-Head Compare",
            "🎯 JD Intelligence",
        ]
    )

    # -------------------------------------------------------------
    # TAB 1: LEADERBOARD & INTERACTIVE ANALYTICS
    # -------------------------------------------------------------
    with tab_leaderboard:
        st.markdown("### 🏅 Candidate Ranking & Factor Breakdown")

        # Interactive Filters
        f_col1, f_col2 = st.columns([1, 2])
        with f_col1:
            min_score_filter = st.slider("Filter by Minimum Final Score:", 0.0, 100.0, 0.0, 5.0)
        with f_col2:
            all_detected_skills = sorted(list({s for r in results for s in r.matched_skills}))
            skill_filter = st.multiselect(
                "Filter Candidates possessing specific skills:",
                options=all_detected_skills,
                placeholder="Select skills (e.g., Python, Docker)...",
            )

        # Apply filters
        filtered_results = [r for r in results if r.final_score >= min_score_filter]
        if skill_filter:
            filtered_results = [
                r for r in filtered_results if all(s in r.matched_skills for s in skill_filter)
            ]

        if not filtered_results:
            st.warning("No candidates match the selected filters. Try lowering the threshold or clearing skills.")
        else:
            # Interactive Factor Comparison Chart with Blue/Emerald palette
            chart_data = []
            for r in filtered_results:
                chart_data.extend(
                    [
                        {"Candidate": r.filename[:20], "Component": "Semantic", "Score": r.semantic_score},
                        {
                            "Candidate": r.filename[:20],
                            "Component": "Skill Match (%)",
                            "Score": r.skill_score if r.skill_score is not None else 0.0,
                        },
                        {"Candidate": r.filename[:20], "Component": "Experience", "Score": r.experience_section_score},
                        {"Candidate": r.filename[:20], "Component": "Lexical", "Score": r.lexical_score},
                    ]
                )

            chart_df = pd.DataFrame(chart_data)
            bar_chart = (
                alt.Chart(chart_df)
                .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X("Component:N", title=None),
                    y=alt.Y("Score:Q", title="Score (0-100)", scale=alt.Scale(domain=[0, 100])),
                    color=alt.Color(
                        "Component:N",
                        scale=alt.Scale(
                            domain=["Semantic", "Skill Match (%)", "Experience", "Lexical"],
                            range=["#2563EB", "#059669", "#D97706", "#0284C7"],
                        ),
                        legend=alt.Legend(title="Factor Component", orient="top"),
                    ),
                    column=alt.Column("Candidate:N", title=None),
                    tooltip=["Candidate", "Component", alt.Tooltip("Score:Q", format=".1f")],
                )
                .properties(height=280)
            )
            st.altair_chart(bar_chart, use_container_width=True)

            # Leaderboard Table
            df_filtered = results_to_dataframe(filtered_results)
            display_cols = [
                "Rank", "Candidate File", "Final Score", "Skill Match (%)",
                "Semantic Score", "Experience Score", "Lexical Score"
            ]
            st.dataframe(
                df_filtered[display_cols],
                use_container_width=True,
                hide_index=True,
            )

        # Downloads
        st.markdown("#### 📥 Export Assessment Reports")
        csv_data = generate_csv_report(results)
        json_data = generate_json_report(results)

        d1, d2, _ = st.columns([1, 1, 2])
        with d1:
            st.download_button(
                label="📄 Download CSV Report",
                data=csv_data.encode("utf-8"),
                file_name="resume_rankings.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_download_csv",
            )
        with d2:
            st.download_button(
                label="📦 Download JSON Report",
                data=json_data.encode("utf-8"),
                file_name="resume_rankings.json",
                mime="application/json",
                use_container_width=True,
                key="btn_download_json",
            )

    # -------------------------------------------------------------
    # TAB 2: CANDIDATE DEEP DIVE
    # -------------------------------------------------------------
    with tab_deepdive:
        candidate_names = [f"#{i+1} {r.filename} ({r.final_score:.1f}/100)" for i, r in enumerate(results)]
        selected_cand_idx = st.selectbox(
            "Select Candidate to Inspect:",
            options=range(len(results)),
            format_func=lambda idx: candidate_names[idx],
        )

        res = results[selected_cand_idx]
        rank_num = selected_cand_idx + 1

        st.markdown(
            f"### #{rank_num} {res.filename} {get_tier_badge(res.final_score)}",
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.markdown("#### 📊 Score Decomposition")
            st.write(f"• **Semantic Similarity:** `{res.semantic_score:.1f}/100`")
            skill_str = f"`{res.skill_score:.1f}%`" if res.skill_score is not None else "`N/A`"
            st.write(f"• **Skill Match Coverage:** {skill_str}")
            st.write(f"• **Experience Relevance:** `{res.experience_section_score:.1f}/100`")
            st.write(f"• **Lexical (TF-IDF):** `{res.lexical_score:.1f}/100`")
            st.progress(min(1.0, res.final_score / 100.0))

        with col_b:
            st.markdown("#### 📑 Section-by-Section Alignment")
            if res.section_scores:
                sec_cols = st.columns(min(len(res.section_scores), 4))
                for idx, (s_name, s_score) in enumerate(res.section_scores.items()):
                    target_col = sec_cols[idx % len(sec_cols)]
                    target_col.metric(s_name.title(), f"{s_score:.1f}/100")
            else:
                st.caption("No individual sections detected (full text analyzed).")

        st.markdown("---")
        st.markdown("#### 🎯 Skills Matrix Breakdown")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"**Matched JD Skills ({len(res.matched_skills)}):**")
            st.markdown(render_skill_badges(res.matched_skills, "green"), unsafe_allow_html=True)
        with m2:
            st.markdown(f"**Missing JD Skills ({len(res.missing_skills)}):**")
            st.markdown(render_skill_badges(res.missing_skills, "red"), unsafe_allow_html=True)
        with m3:
            st.markdown(f"**Additional Detected Skills ({len(res.extra_skills)}):**")
            st.markdown(render_skill_badges(res.extra_skills, "blue"), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 💡 Tailoring Feedback & Actionable Gaps")
        if res.suggestions:
            for tip in res.suggestions:
                st.info(f"👉 {tip}")
        else:
            st.success("🌟 No critical gaps identified — strong alignment with target profile!")

    # -------------------------------------------------------------
    # TAB 3: HEAD-TO-HEAD COMPARISON
    # -------------------------------------------------------------
    with tab_head2head:
        if len(results) < 2:
            st.info("Upload at least two resumes (or run the demo) to enable side-by-side head-to-head comparison.")
        else:
            h_c1, h_c2 = st.columns(2)
            with h_c1:
                cand_a_idx = st.selectbox(
                    "Select Candidate A:",
                    options=range(len(results)),
                    index=0,
                    format_func=lambda idx: f"{results[idx].filename} ({results[idx].final_score:.1f})",
                    key="select_cand_a",
                )
            with h_c2:
                cand_b_idx = st.selectbox(
                    "Select Candidate B:",
                    options=range(len(results)),
                    index=1 if len(results) > 1 else 0,
                    format_func=lambda idx: f"{results[idx].filename} ({results[idx].final_score:.1f})",
                    key="select_cand_b",
                )

            render_head_to_head(results[cand_a_idx], results[cand_b_idx])

    # -------------------------------------------------------------
    # TAB 4: JOB DESCRIPTION INTELLIGENCE
    # -------------------------------------------------------------
    with tab_jd:
        st.markdown("### 🎯 Target Job Description Analysis")
        raw_jd_str = jd_content.decode("utf-8", errors="ignore") if isinstance(jd_content, bytes) else str(jd_content)
        detected_jd_skills = skill_extractor.extract_skills(raw_jd_str)
        grouped_jd_skills = skill_extractor.group_skills_by_category(detected_jd_skills)

        st.markdown(f"**Total Required Skills Identified:** `{len(detected_jd_skills)}`")

        if grouped_jd_skills:
            g_cols = st.columns(min(len(grouped_jd_skills), 3))
            for i, (cat_name, cat_skills) in enumerate(grouped_jd_skills.items()):
                target_col = g_cols[i % len(g_cols)]
                with target_col:
                    st.markdown(f"**{cat_name.title()} ({len(cat_skills)})**")
                    st.markdown(render_skill_badges(cat_skills, "green"), unsafe_allow_html=True)
        else:
            st.caption("No taxonomy skills detected in Job Description.")

        with st.expander("📄 View Full Job Description Text"):
            st.text(raw_jd_str)


if __name__ == "__main__":
    main()
