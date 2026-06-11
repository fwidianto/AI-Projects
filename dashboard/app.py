"""Streamlit Dashboard for AI Job Intelligence Platform."""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.database import get_db, init_db
from src.models.profile import Profile
from src.services.job_service import JobService
from src.services.scoring_service import ScoringService
from src.services.report_service import ReportService

# Page config
st.set_page_config(
    page_title="AI Job Intelligence Platform",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# Custom CSS
# =============================================================================

st.markdown("""
<style>
    .job-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 15px;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #dee2e6;
    }
    .score-excellent { color: #28a745; font-weight: bold; }
    .score-good { color: #17a2b8; font-weight: bold; }
    .score-moderate { color: #ffc107; font-weight: bold; }
    .score-low { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Session State
# =============================================================================

def init_session():
    """Initialize session state."""
    if "profile_id" not in st.session_state:
        st.session_state.profile_id = None
    if "db" not in st.session_state:
        st.session_state.db = next(get_db())


# =============================================================================
# Sidebar
# =============================================================================

def render_sidebar():
    """Render sidebar navigation."""
    st.sidebar.title("💼 Job Intelligence")
    st.sidebar.markdown("---")
    
    # Profile selector
    st.sidebar.subheader("Profile")
    db = next(get_db())
    profiles = db.query(Profile).filter(Profile.is_active == True).all()
    
    profile_options = {p.name: p.id for p in profiles}
    profile_options["Create New Profile"] = "new"
    
    selected_profile = st.sidebar.selectbox(
        "Select Profile",
        options=list(profile_options.keys()),
        index=0 if profiles else 0,
    )
    
    if selected_profile == "Create New Profile":
        st.sidebar.info("Go to Settings to create a new profile")
    else:
        st.session_state.profile_id = profile_options.get(selected_profile)
    
    st.sidebar.markdown("---")
    
    # Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["📊 Dashboard", "💼 Jobs", "📈 Analytics", "⚙️ Settings"],
        label_visibility="collapsed",
    )
    
    return page


# =============================================================================
# Dashboard Page
# =============================================================================

def render_dashboard():
    """Render main dashboard page."""
    st.title("📊 Dashboard")
    
    if not st.session_state.profile_id:
        st.warning("Please select a profile from the sidebar to view your job matches.")
        return
    
    profile_id = st.session_state.profile_id
    db = next(get_db())
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    report_service = ReportService(db)
    stats = report_service.get_dashboard_stats(profile_id)
    
    with col1:
        st.metric("Total Jobs", stats["total_jobs"])
    with col2:
        st.metric("Scored", stats["total_scores"])
    with col3:
        st.metric("Applied", stats["applied"])
    with col4:
        st.metric("Avg Score", f"{stats['avg_score']:.1f}%")
    
    st.markdown("---")
    
    # Score Distribution
    st.subheader("Score Distribution")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Score chart
        score_data = stats["score_distribution"]
        chart_data = {
            "Score Range": list(score_data.keys()),
            "Count": list(score_data.values()),
        }
        st.bar_chart(chart_data, x="Score Range", y="Count")
    
    with col2:
        st.write("**Score Ranges:**")
        for range_name, count in score_data.items():
            color = {
                "90+": "🟢",
                "80-89": "🟢",
                "70-79": "🟡",
                "60-69": "🟡",
                "50-59": "🟠",
                "<50": "🔴",
            }.get(range_name, "⚪")
            st.write(f"{color} {range_name}: {count}")
    
    st.markdown("---")
    
    # Top Matches
    st.subheader("🎯 Top Job Matches")
    
    scoring_service = ScoringService(db)
    top_jobs = scoring_service.get_top_jobs(profile_id, limit=10, min_score=50)
    
    if not top_jobs:
        st.info("No job matches found. Try scoring more jobs or lowering the score threshold.")
    else:
        for item in top_jobs:
            job = item["job"]
            score = item["score"]
            
            score_color = {
                "Excellent Match": "score-excellent",
                "Strong Match": "score-good",
                "Good Match": "score-moderate",
                "Moderate Match": "score-low",
            }.get(score["score_label"], "")
            
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"### {job['title']}")
                    st.write(f"**Company:** {job['company']}")
                    st.write(f"**Location:** {job['location'] or 'N/A'} {'🌐 (Remote)' if job['is_remote'] else ''}")
                    st.write(f"**Salary:** {job['salary_display']}")
                
                with col2:
                    st.markdown(f"### <span class='{score_color}'>{score['total_score']:.1f}%</span>", unsafe_allow_html=True)
                    st.write(f"**{score['score_label']}**")
                
                with col3:
                    if job['apply_url']:
                        st.markdown(f"[Apply Now]({job['apply_url']})")
                    st.write(f"📅 {job['age_display']}")
                
                # Matched skills
                matched = score.get("matched_skills", [])
                if matched:
                    st.write(f"✅ **Matched:** {', '.join(matched[:5])}")
                
                missing = score.get("missing_skills", [])
                if missing:
                    st.write(f"❌ **Missing:** {', '.join(missing[:3])}")
                
                st.markdown("---")


# =============================================================================
# Jobs Page
# =============================================================================

def render_jobs():
    """Render jobs listing page."""
    st.title("💼 Job Listings")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("Search", placeholder="Job title, company, skills...")
    
    with col2:
        location_filter = st.selectbox(
            "Location",
            ["All", "Jakarta", "Bekasi", "Karawang", "Remote"]
        )
    
    with col3:
        score_filter = st.slider("Min Score", 0, 100, 50)
    
    # Get jobs
    db = next(get_db())
    job_service = JobService(db)
    
    jobs = job_service.search_jobs(
        query=search_query if search_query else None,
        location=location_filter if location_filter != "All" else None,
        limit=50,
    )
    
    st.write(f"**{len(jobs)} jobs found**")
    
    # Display jobs
    for job in jobs:
        with st.expander(f"📋 {job.title} - {job.company}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Location:** {job.location or 'N/A'}")
                st.write(f"**Salary:** {job.salary_range_display}")
                st.write(f"**Type:** {job.employment_type or 'Not specified'}")
                st.write(f"**Posted:** {job.age_display}")
                
                if job.description:
                    st.write("---")
                    st.write(job.description[:500] + "..." if len(job.description) > 500 else job.description)
            
            with col2:
                st.write(f"**Source:** {job.source_obj.name if job.source_obj else 'N/A'}")
                if job.apply_url:
                    st.markdown(f"[Apply Link]({job.apply_url})")
                
                # Mark as applied
                if st.button(f"Mark as Applied", key=f"apply_{job.id}"):
                    job.is_applied = True
                    db.commit()
                    st.success("Marked as applied!")


# =============================================================================
# Analytics Page
# =============================================================================

def render_analytics():
    """Render analytics page."""
    st.title("📈 Analytics")
    
    if not st.session_state.profile_id:
        st.warning("Please select a profile from the sidebar.")
        return
    
    profile_id = st.session_state.profile_id
    db = next(get_db())
    
    report_service = ReportService(db)
    stats = report_service.get_dashboard_stats(profile_id)
    
    # Location breakdown
    st.subheader("Jobs by Location")
    location_data = stats["location_breakdown"]
    
    if location_data:
        st.bar_chart({"Location": list(location_data.keys()), "Count": list(location_data.values())})
    else:
        st.info("No location data available yet.")
    
    st.markdown("---")
    
    # Skills in demand
    st.subheader("🔥 Skills in Demand")
    skills = stats["top_skills_in_demand"]
    
    if skills:
        # Display as tags
        cols = st.columns(4)
        for i, skill in enumerate(skills):
            with cols[i % 4]:
                st.markdown(f"- **{skill}**")
    else:
        st.info("No skills data available yet.")


# =============================================================================
# Settings Page
# =============================================================================

def render_settings():
    """Render settings page."""
    st.title("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["Profile", "Scrapers", "About"])
    
    with tab1:
        st.subheader("Profile Management")
        
        # Create new profile form
        with st.form("create_profile"):
            st.write("### Create New Profile")
            
            name = st.text_input("Name *")
            email = st.text_input("Email")
            headline = st.text_input("Headline")
            
            target_roles = st.multiselect(
                "Target Roles",
                [
                    "ERP Analyst", "Business Analyst", "Operations Analyst",
                    "Cost Control Analyst", "Finance Analyst",
                    "Reporting Analyst", "Data Analyst",
                ],
            )
            
            locations = st.multiselect(
                "Preferred Locations",
                ["Jakarta", "Bekasi", "Karawang", "Remote"],
                default=["Jakarta", "Remote"],
            )
            
            col1, col2 = st.columns(2)
            with col1:
                salary_min = st.number_input("Min Salary (IDR)", 0, 100_000_000, 15_000_000, step=1_000_000)
            with col2:
                salary_max = st.number_input("Max Salary (IDR)", 0, 100_000_000, 25_000_000, step=1_000_000)
            
            skills = st.text_area("Skills (comma separated)", placeholder="SAP, SQL, Python, ...")
            
            submitted = st.form_submit_button("Create Profile")
            
            if submitted and name:
                import json
                
                db = next(get_db())
                
                profile = Profile(
                    name=name,
                    email=email or None,
                    headline=headline or None,
                    target_roles=json.dumps(target_roles),
                    preferred_locations=json.dumps(locations),
                    salary_min=salary_min,
                    salary_max=salary_max,
                )
                
                db.add(profile)
                db.commit()
                st.success("Profile created successfully!")
    
    with tab2:
        st.subheader("Scraper Configuration")
        st.write("Configure which job board scrapers to enable.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_indeed = st.checkbox("Enable Indeed Scraper", value=True)
            enable_glints = st.checkbox("Enable Glints Scraper", value=True)
        
        with col2:
            enable_jobstreet = st.checkbox("Enable JobStreet Scraper", value=True)
            enable_linkedin = st.checkbox("Enable LinkedIn Scraper", value=False)
        
        if st.button("Save Configuration"):
            st.info("Configuration saved! (Persistence coming soon)")
    
    with tab3:
        st.subheader("About")
        st.write("""
        **AI Job Intelligence Platform**
        
        Version: 0.1.0
        
        This platform helps you:
        - Discover jobs matching your profile
        - Score jobs based on skills and requirements
        - Track your job applications
        - Generate personalized reports
        """)


# =============================================================================
# Main
# =============================================================================

def main():
    """Main entry point."""
    init_session()
    
    # Initialize database
    init_db()
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Render selected page
    if page == "📊 Dashboard":
        render_dashboard()
    elif page == "💼 Jobs":
        render_jobs()
    elif page == "📈 Analytics":
        render_analytics()
    elif page == "⚙️ Settings":
        render_settings()


if __name__ == "__main__":
    main()