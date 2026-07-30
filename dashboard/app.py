import streamlit as st
from frontend.styles import apply_enterprise_styles
from frontend.pages.home import render_home_page
from frontend.pages.assistant import render_assistant_page
from frontend.pages.dashboard_page import render_dashboard_page
from frontend.pages.audit_logs_page import render_audit_logs_page
from frontend.pages.analytics_page import render_analytics_page

# Configure Page Layout and Theme
st.set_page_config(
    page_title="Enterprise AI Governance Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Enterprise SaaS Design System CSS
apply_enterprise_styles()

# Sidebar Brand Header & Navigation
st.sidebar.markdown("## 🛡️ **AI Governance**")
st.sidebar.caption("Enterprise Zero-Trust Platform v2.0")
st.sidebar.divider()

page_selection = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home & Architecture",
        "🤖 AI Customer Assistant",
        "📊 Governance Dashboard",
        "📜 Audit Logs Explorer",
        "📈 Agent Analytics & Threats"
    ],
    index=0
)

st.sidebar.divider()
st.sidebar.markdown("""
<div style="font-size:0.75rem; color:#6b7280; text-align:center;">
    Tool Permission Enforcer Proxy<br/>
    FastAPI • SQLite • Gemini 2.5 Flash<br/>
    ABAC Policy Engine Active
</div>
""", unsafe_allow_html=True)

# Route to Selected Page
if page_selection == "🏠 Home & Architecture":
    render_home_page()
elif page_selection == "🤖 AI Customer Assistant":
    render_assistant_page()
elif page_selection == "📊 Governance Dashboard":
    render_dashboard_page()
elif page_selection == "📜 Audit Logs Explorer":
    render_audit_logs_page()
elif page_selection == "📈 Agent Analytics & Threats":
    render_analytics_page()
