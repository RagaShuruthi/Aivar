import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# 20 Predefined CRM Users matching SQLite Mock CRM
PREDEFINED_USERS_LOGIN = {
    101: {"id": 101, "customer_id": 101, "name": "Shruthi", "department": "Support", "role": "support_agent", "role_title": "Support"},
    102: {"id": 102, "customer_id": 102, "name": "Kavin", "department": "Sales", "role": "sales_agent", "role_title": "Sales"},
    103: {"id": 103, "customer_id": 103, "name": "Sabari", "department": "Finance", "role": "support_agent", "role_title": "Finance"},
    104: {"id": 104, "customer_id": 104, "name": "Elaki", "department": "HR", "role": "support_agent", "role_title": "HR"},
    105: {"id": 105, "customer_id": 105, "name": "Harini", "department": "Sales", "role": "sales_agent", "role_title": "Sales"},
    106: {"id": 106, "customer_id": 106, "name": "Vignesh", "department": "Support", "role": "support_agent", "role_title": "Support"},
    107: {"id": 107, "customer_id": 107, "name": "Akash", "department": "Sales", "role": "sales_agent", "role_title": "Sales"},
    108: {"id": 108, "customer_id": 108, "name": "Priya", "department": "HR", "role": "support_agent", "role_title": "HR"},
    109: {"id": 109, "customer_id": 109, "name": "Naveen", "department": "Finance", "role": "support_agent", "role_title": "Finance"},
    110: {"id": 110, "customer_id": 110, "name": "Keerthana", "department": "Support", "role": "support_agent", "role_title": "Support"},
    111: {"id": 111, "customer_id": 111, "name": "Rahul", "department": "Sales", "role": "sales_agent", "role_title": "Sales"},
    112: {"id": 112, "customer_id": 112, "name": "Nisha", "department": "Support", "role": "support_agent", "role_title": "Support"},
    113: {"id": 113, "customer_id": 113, "name": "Dinesh", "department": "Manager", "role": "sales_agent", "role_title": "Manager"},
    114: {"id": 114, "customer_id": 114, "name": "Kavya", "department": "Support", "role": "support_agent", "role_title": "Support"},
    115: {"id": 115, "customer_id": 115, "name": "Arjun", "department": "Sales", "role": "sales_agent", "role_title": "Sales"},
    116: {"id": 116, "customer_id": 116, "name": "Deepika", "department": "Finance", "role": "support_agent", "role_title": "Finance"},
    117: {"id": 117, "customer_id": 117, "name": "Sanjay", "department": "Support", "role": "support_agent", "role_title": "Support"},
    118: {"id": 118, "customer_id": 118, "name": "Meena", "department": "HR", "role": "support_agent", "role_title": "HR"},
    119: {"id": 119, "customer_id": 119, "name": "Ashwin", "department": "Sales", "role": "sales_agent", "role_title": "Sales"},
    120: {"id": 120, "customer_id": 120, "name": "Divya", "department": "Admin", "role": "admin_agent", "role_title": "Admin"},
}

ROLE_MAP = {
    "Read Only Agent": {"role": "support_agent", "role_title": "Read Only Agent"},
    "Read + Update Agent": {"role": "sales_agent", "role_title": "Read + Update Agent"},
    "Full Access Agent": {"role": "admin_agent", "role_title": "Full Access Agent"},
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

def login_user_and_clear_session(user_data):
    """Sets session user state and wipes previous chat/trace history completely."""
    st.session_state.authenticated = True
    st.session_state.user = user_data
    st.session_state.messages = []
    st.session_state.last_pipeline_response = None
    st.query_params["cid"] = str(user_data["customer_id"])
    st.rerun()

def render_login_page():
    """Renders Session Context Initialization Page collecting User Name, Agent Role, and Session Customer Scope."""
    if auto_login_from_query_params():
        return

    st.markdown("""
    <style>
    .init-card {
        background: rgba(17, 24, 39, 0.85);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.markdown(
            '<div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">'
            '<h1 style="background: linear-gradient(135deg, #60a5fa 0%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 6px;">Session Context Initialization</h1>'
            '<p style="color: #9ca3af; font-size: 0.95rem;">Configure user identity and session scope for the Permission Proxy PDP</p>'
            '</div>',
            unsafe_allow_html=True
        )

        with st.container():
            user_name = st.text_input("User Name", value="Shruthi", key="init_user_name")
            
            selected_role_label = st.selectbox(
                "User Role",
                ["Read Only Agent", "Read + Update Agent", "Full Access Agent"],
                index=0,
                key="init_user_role"
            )

            
            customer_scope_id = st.number_input(
                "Session Customer Scope (Customer ID)",
                min_value=101,
                max_value=999,
                value=101,
                step=1,
                key="init_customer_scope"
            )

            st.markdown("<br/>", unsafe_allow_html=True)

            if st.button("Initialize Session Context", use_container_width=True, key="btn_init_session"):
                role_info = ROLE_MAP[selected_role_label]
                user_data = {
                    "id": int(customer_scope_id),
                    "customer_id": int(customer_scope_id),
                    "name": user_name.strip() if user_name.strip() else "User",
                    "department": selected_role_label,
                    "role": role_info["role"],
                    "role_title": role_info["role_title"]
                }
                login_user_and_clear_session(user_data)

        st.divider()
        st.markdown("#### **Preset Session Scenarios**")
        q_col1, q_col2, q_col3 = st.columns(3)

        if q_col1.button("Read Only (ID 101)", use_container_width=True, key="quick_101"):
            login_user_and_clear_session({
                "id": 101, "customer_id": 101, "name": "Shruthi", "department": "Support",
                "role": "support_agent", "role_title": "Read Only Agent"
            })

        if q_col2.button("Read + Update (ID 102)", use_container_width=True, key="quick_102"):
            login_user_and_clear_session({
                "id": 102, "customer_id": 102, "name": "Kavin", "department": "Sales",
                "role": "sales_agent", "role_title": "Read + Update Agent"
            })

        if q_col3.button("Full Access (ID 120)", use_container_width=True, key="quick_120"):
            login_user_and_clear_session({
                "id": 120, "customer_id": 120, "name": "Divya", "department": "Admin",
                "role": "admin_agent", "role_title": "Full Access Agent"
            })


