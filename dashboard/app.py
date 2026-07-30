import streamlit as st
from frontend.styles import apply_enterprise_styles
from frontend.pages.login import render_login_page
from frontend.pages.assistant import render_assistant_page
from frontend.pages.dashboard_page import render_dashboard_page
from frontend.pages.audit_logs_page import render_audit_logs_page
from frontend.pages.analytics_page import render_analytics_page

# Configure Page Layout and Theme
st.set_page_config(
    page_title="Enterprise AI CRM Assistant & Governance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Enterprise SaaS Design System CSS
apply_enterprise_styles()

# Check Authentication Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Render Login Page if unauthenticated
if not st.session_state.authenticated:
    render_login_page()
else:
    user = st.session_state.get("user", {
        "name": "Alice Smith",
        "email": "alice@enterprise.com",
        "role": "support_agent",
        "role_title": "Customer Support",
        "customer_id": 101
    })

    # Sidebar Brand Header & Session Profile Badge
    st.sidebar.markdown("## 🛡️ **AI Governance**")
    st.sidebar.caption("Enterprise Zero-Trust Platform v2.0")
    st.sidebar.divider()

    # Logged-In User Profile Card
    st.sidebar.markdown(f"""
    <div style="background: rgba(31, 41, 55, 0.7); border: 1px solid #374151; border-radius: 10px; padding: 12px; margin-bottom: 15px;">
        <div style="font-weight: bold; color: #f3f4f6; font-size: 0.95rem;">👤 {user['name']}</div>
        <div style="color: #60a5fa; font-size: 0.8rem; font-weight: 600;">{user['role_title']}</div>
        <div style="color: #9ca3af; font-size: 0.75rem; margin-top: 4px;">Session CID: <b>#{user['customer_id']}</b></div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🚪 Sign Out", use_container_width=True, key="btn_sign_out"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.messages = []
        st.rerun()

    st.sidebar.divider()

    page_selection = st.sidebar.radio(
        "Navigation",
        [
            "💬 AI CRM Assistant",
            "📊 Governance SOC Dashboard",
            "📜 Audit Logs Explorer",
            "📈 Agent Analytics & Threats"
        ],
        index=0,
        key="main_sidebar_navigation_radio"
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
    if page_selection == "💬 AI CRM Assistant":
        render_assistant_page()
    elif page_selection == "📊 Governance SOC Dashboard":
        render_dashboard_page()
    elif page_selection == "📜 Audit Logs Explorer":
        render_audit_logs_page()
    elif page_selection == "📈 Agent Analytics & Threats":
        render_analytics_page()
