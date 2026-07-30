import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# Hardcoded fallback user mapping matching mock CRM database for offline resilience
MOCK_USERS_MAP = {
    # CRM Administrator
    "shuruthi": {"name": "Shuruthi", "role": "admin_agent", "role_title": "CRM Administrator", "customer_id": 101, "email": "shuruthi@crm.com", "department": "Executive Management", "city": "Boston"},
    "kavin": {"name": "Kavin", "role": "admin_agent", "role_title": "CRM Administrator", "customer_id": 102, "email": "kavin@crm.com", "department": "IT Infrastructure", "city": "Seattle"},
    "sabari": {"name": "Sabari", "role": "admin_agent", "role_title": "CRM Administrator", "customer_id": 103, "email": "sabari@crm.com", "department": "Database Administration", "city": "Austin"},
    
    # Support Agent
    "elakiya": {"name": "Elakiya", "role": "support_agent", "role_title": "Support Agent", "customer_id": 104, "email": "elakiya@crm.com", "department": "Customer Operations", "city": "San Jose"},
    "koushik": {"name": "Koushik", "role": "support_agent", "role_title": "Support Agent", "customer_id": 105, "email": "koushik@crm.com", "department": "Technical Support", "city": "Chicago"},
    "nithin": {"name": "Nithin", "role": "support_agent", "role_title": "Support Agent", "customer_id": 106, "email": "nithin@crm.com", "department": "Client Success", "city": "New York"},
    "raashmi": {"name": "Raashmi", "role": "support_agent", "role_title": "Support Agent", "customer_id": 107, "email": "raashmi@crm.com", "department": "Customer Care", "city": "Atlanta"},
    "mousi": {"name": "Mousi", "role": "support_agent", "role_title": "Support Agent", "customer_id": 108, "email": "mousi@crm.com", "department": "Help Desk", "city": "Denver"},

    # Read Only
    "ragul": {"name": "Ragul", "role": "restricted_agent", "role_title": "Read Only", "customer_id": 109, "email": "ragul@crm.com", "department": "Compliance & Legal", "city": "San Francisco"},
    "saran": {"name": "Saran", "role": "restricted_agent", "role_title": "Read Only", "customer_id": 110, "email": "saran@crm.com", "department": "Financial Audit", "city": "Dallas"},
    "kanika": {"name": "Kanika", "role": "restricted_agent", "role_title": "Read Only", "customer_id": 111, "email": "kanika@crm.com", "department": "Risk Analytics", "city": "Los Angeles"},
    "malini": {"name": "Malini", "role": "restricted_agent", "role_title": "Read Only", "customer_id": 112, "email": "malini@crm.com", "department": "Quality Assurance", "city": "Miami"},
    "malleshwar": {"name": "Malleshwar", "role": "restricted_agent", "role_title": "Read Only", "customer_id": 113, "email": "malleshwar@crm.com", "department": "Internal Audit", "city": "Phoenix"},
    "kelwin": {"name": "Kelwin", "role": "restricted_agent", "role_title": "Read Only", "customer_id": 114, "email": "kelwin@crm.com", "department": "Security Review", "city": "Portland"},
    "vivna": {"name": "Vivna", "role": "restricted_agent", "role_title": "Read Only", "customer_id": 115, "email": "vivna@crm.com", "department": "Regulatory Affairs", "city": "San Diego"},
    "dhanya": {"name": "Dhanya", "role": "restricted_agent", "role_title": "Read Only", "customer_id": 116, "email": "dhanya@crm.com", "department": "Data Governance", "city": "Seattle"},
    "sakthi": {"name": "Sakthi", "role": "restricted_agent", "role_title": "Read Only", "customer_id": 117, "email": "sakthi@crm.com", "department": "Reporting", "city": "Houston"},
    "santhosh": {"name": "Santhosh", "role": "restricted_agent", "role_title": "Read Only", "customer_id": 118, "email": "santhosh@crm.com", "department": "Business Intelligence", "city": "Detroit"},
    "rithish": {"name": "Rithish", "role": "restricted_agent", "role_title": "Read Only", "customer_id": 119, "email": "rithish@crm.com", "department": "Product Research", "city": "Minneapolis"},
    "sanjay": {"name": "Sanjay", "role": "restricted_agent", "role_title": "Read Only", "customer_id": 120, "email": "sanjay@crm.com", "department": "Security Operations", "city": "Raleigh"},
}

def render_login_page():
    """Renders simple Demo Login page accepting ONLY Name and Role."""
    st.markdown("""
    <style>
    .login-card {
        max-width: 480px;
        margin: 30px auto;
        padding: 35px;
        background: rgba(17, 24, 39, 0.9);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align: center; margin-bottom: 25px;">'
        '<h1 style="background: linear-gradient(135deg, #60a5fa 0%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.4rem; font-weight: 800; margin-bottom: 5px;">🛡️ Enterprise AI CRM</h1>'
        '<p style="color: #9ca3af; font-size: 0.95rem;">Demonstration Login Gateway</p>'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔑 Demo Login")
        st.caption("Please enter your name and select your registered role.")
        
        # 1. Name Text Input
        name_input = st.text_input("Name", value="", placeholder="e.g. Shuruthi, Elakiya, Ragul", key="demo_name_input")
        
        # 2. Role Dropdown
        selected_role_title = st.selectbox(
            "Role",
            ["CRM Administrator", "Support Agent", "Read Only"],
            key="demo_role_select"
        )

        st.markdown("<br/>", unsafe_allow_html=True)

        # 3. Login Button
        if st.button("🚀 Login", use_container_width=True, key="demo_login_button"):
            name_clean = name_input.strip()
            if not name_clean:
                st.error("Invalid Name or Role.")
            else:
                user_found = None
                # Call backend auth route first
                try:
                    res = requests.post(f"{API_BASE_URL}/auth/demo-login", json={"name": name_clean, "role": selected_role_title}, timeout=4)
                    if res.status_code == 200:
                        user_found = res.json()
                except Exception:
                    pass

                # Fallback to local map if backend connection times out
                if not user_found:
                    user_info = MOCK_USERS_MAP.get(name_clean.lower())
                    if user_info and user_info["role_title"].lower() == selected_role_title.lower():
                        user_found = user_info

                if user_found:
                    st.session_state.authenticated = True
                    st.session_state.user = user_found
                    st.success(f"Welcome, {user_found['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid Name or Role.")

        st.divider()

        # Quick Reference Guide for Demo Testers
        with st.expander("📋 View Valid Demo Users"):
            st.markdown("""
            **CRM Administrator** *(Read, Update, Delete)*:
            - `Shuruthi`, `Kavin`, `Sabari`
            
            **Support Agent** *(Read, Update)*:
            - `Elakiya`, `Koushik`, `Nithin`, `Raashmi`, `Mousi`
            
            **Read Only** *(Read)*:
            - `Ragul`, `Saran`, `Kanika`, `Malini`, `Malleshwar`, `Kelwin`, `Vivna`, `Dhanya`, `Sakthi`, `Santhosh`, `Rithish`, `Sanjay`
            """)
