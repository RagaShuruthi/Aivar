import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# 20 Predefined CRM Users matching SQLite Mock CRM
PREDEFINED_USERS_LOGIN = {
    101: {"id": 101, "customer_id": 101, "name": "Shruthi", "department": "Support", "role": "support_agent", "role_title": "Support Agent"},
    102: {"id": 102, "customer_id": 102, "name": "Kavin", "department": "Sales", "role": "sales_agent", "role_title": "Sales Agent"},
    103: {"id": 103, "customer_id": 103, "name": "Sabari", "department": "Finance", "role": "support_agent", "role_title": "Support Agent"},
    104: {"id": 104, "customer_id": 104, "name": "Elaki", "department": "HR", "role": "support_agent", "role_title": "Support Agent"},
    105: {"id": 105, "customer_id": 105, "name": "Harini", "department": "Sales", "role": "sales_agent", "role_title": "Sales Agent"},
    106: {"id": 106, "customer_id": 106, "name": "Vignesh", "department": "Support", "role": "support_agent", "role_title": "Support Agent"},
    107: {"id": 107, "customer_id": 107, "name": "Akash", "department": "Sales", "role": "sales_agent", "role_title": "Sales Agent"},
    108: {"id": 108, "customer_id": 108, "name": "Priya", "department": "HR", "role": "support_agent", "role_title": "Support Agent"},
    109: {"id": 109, "customer_id": 109, "name": "Naveen", "department": "Finance", "role": "support_agent", "role_title": "Support Agent"},
    110: {"id": 110, "customer_id": 110, "name": "Keerthana", "department": "Support", "role": "support_agent", "role_title": "Support Agent"},
    111: {"id": 111, "customer_id": 111, "name": "Rahul", "department": "Sales", "role": "sales_agent", "role_title": "Sales Agent"},
    112: {"id": 112, "customer_id": 112, "name": "Nisha", "department": "Support", "role": "support_agent", "role_title": "Support Agent"},
    113: {"id": 113, "customer_id": 113, "name": "Dinesh", "department": "Manager", "role": "sales_agent", "role_title": "Sales Agent"},
    114: {"id": 114, "customer_id": 114, "name": "Kavya", "department": "Support", "role": "support_agent", "role_title": "Support Agent"},
    115: {"id": 115, "customer_id": 115, "name": "Arjun", "department": "Sales", "role": "sales_agent", "role_title": "Sales Agent"},
    116: {"id": 116, "customer_id": 116, "name": "Deepika", "department": "Finance", "role": "support_agent", "role_title": "Support Agent"},
    117: {"id": 117, "customer_id": 117, "name": "Sanjay", "department": "Support", "role": "support_agent", "role_title": "Support Agent"},
    118: {"id": 118, "customer_id": 118, "name": "Meena", "department": "HR", "role": "support_agent", "role_title": "Support Agent"},
    119: {"id": 119, "customer_id": 119, "name": "Ashwin", "department": "Sales", "role": "sales_agent", "role_title": "Sales Agent"},
    120: {"id": 120, "customer_id": 120, "name": "Divya", "department": "Admin", "role": "admin_agent", "role_title": "Admin Agent"},
}

def auto_login_from_query_params():
    """Checks browser query params for persistent session restoration."""
    if "authenticated" in st.session_state and st.session_state.authenticated:
        return True

    params = st.query_params
    if "cid" in params:
        try:
            cid = int(params["cid"])
            if cid in PREDEFINED_USERS_LOGIN:
                st.session_state.authenticated = True
                st.session_state.user = PREDEFINED_USERS_LOGIN[cid]
                return True
        except ValueError:
            pass
    return False

def render_login_page():
    """Renders Enterprise Login Page with Customer ID Authentication & Persistent Storage."""
    if auto_login_from_query_params():
        return

    st.markdown("""
    <style>
    .login-container {
        max-width: 520px;
        margin: 40px auto;
        padding: 40px;
        background: rgba(17, 24, 39, 0.9);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
        text-align: center;
    }
    .role-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-top: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.markdown(
            '<div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">'
            '<h1 style="background: linear-gradient(135deg, #60a5fa 0%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem; font-weight: 800; margin-bottom: 8px;">🛡️ Enterprise AI CRM</h1>'
            '<p style="color: #9ca3af; font-size: 1rem;">Zero-Trust Permission Proxy Gateway</p>'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("### 🔑 **Customer ID Login**")
        st.caption("Enter or select your assigned Customer ID (101 - 120). No password required.")

        # Customer ID Selection / Input
        user_options = {f"Customer #{cid} - {u['name']} ({u['department']} / {u['role_title']})": cid for cid, u in PREDEFINED_USERS_LOGIN.items()}
        selected_user_text = st.selectbox(
            "Select Account to Login:",
            list(user_options.keys()),
            index=0,
            key="login_user_select_box"
        )
        
        selected_cid = user_options[selected_user_text]

        st.markdown("<br/>", unsafe_allow_html=True)

        # Login Action
        if st.button("🚀 Login to Platform", use_container_width=True, key="login_submit_btn"):
            user_data = PREDEFINED_USERS_LOGIN[selected_cid]
            st.session_state.authenticated = True
            st.session_state.user = user_data
            
            # Save session persistently in browser query params
            st.query_params["cid"] = str(selected_cid)
            
            st.success(f"✅ Logged in as {user_data['name']} (#{user_data['customer_id']}) - Role: {user_data['role_title']}")
            st.rerun()

        st.divider()
        st.markdown("#### ⚡ **1-Click Quick Demo Login**")
        q_col1, q_col2, q_col3 = st.columns(3)

        if q_col1.button("👤 Support (#101)", use_container_width=True, key="quick_101"):
            user_data = PREDEFINED_USERS_LOGIN[101]
            st.session_state.authenticated = True
            st.session_state.user = user_data
            st.query_params["cid"] = "101"
            st.rerun()

        if q_col2.button("💼 Sales (#102)", use_container_width=True, key="quick_102"):
            user_data = PREDEFINED_USERS_LOGIN[102]
            st.session_state.authenticated = True
            st.session_state.user = user_data
            st.query_params["cid"] = "102"
            st.rerun()

        if q_col3.button("👑 Admin (#120)", use_container_width=True, key="quick_120"):
            user_data = PREDEFINED_USERS_LOGIN[120]
            st.session_state.authenticated = True
            st.session_state.user = user_data
            st.query_params["cid"] = "120"
            st.rerun()
