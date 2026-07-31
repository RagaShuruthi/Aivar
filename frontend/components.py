import streamlit as st
import requests
from typing import Dict, Any, Optional
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# 20 Predefined CRM Users matching exact system requirements
PREDEFINED_USERS = {
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

def render_left_sidebar():
    """Renders Left Sidebar with Logged-In User Profile Badge & Permission Proxy Status."""
    st.sidebar.markdown("## **Governance & Security**")
    st.sidebar.caption("Zero-Trust Security Gateway v2.0")
    st.sidebar.divider()

    # Retrieve logged-in user from session state
    user = st.session_state.get("user")
    if not user:
        user = PREDEFINED_USERS[101]

    st.sidebar.markdown("### **Session Profile**")
    st.sidebar.markdown(
        f"""
        <div class="glass-card">
            <div style="font-size:0.75rem; color:#9ca3af; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">Session User</div>
            <div style="font-weight:700; font-size:1.15rem; color:#60a5fa;">{user['name']}</div>
            <div style="font-size:0.8rem; color:#9ca3af; margin-top:2px;">ID: {user['customer_id']}</div>
            <div style="font-size:0.85rem; color:#a855f7; font-weight:600; margin-top:6px;">Department: {user['department']}</div>
            <div style="font-size:0.85rem; color:#10b981; font-weight:600; margin-top:2px;">Role: <b>{user['role_title']}</b></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.divider()
    st.sidebar.markdown("### **Policy Gateway Status**")
    st.sidebar.markdown(
        """
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:9px; height:9px; border-radius:50%; background:#10b981; box-shadow: 0 0 10px #10b981;"></div>
            <span style="font-weight:700; color:#10b981; font-size:0.88rem; letter-spacing:0.02em;">GATEWAY ACTIVE</span>
        </div>
        <div style="font-size:0.75rem; color:#9ca3af; margin-top:6px;">
            Zero-Trust access control policy active.
        </div>
        """,
        unsafe_allow_html=True
    )
    return user


def render_customer_card(cdata: Dict[str, Any]):
    """Renders modern Customer Profile Card when allowed."""
    st.markdown(
        f"""
        <div class="glass-card" style="border:1px solid rgba(16, 185, 129, 0.4);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <h3 style="margin:0; color:#10b981; font-size:1.05rem; font-weight:700; letter-spacing:-0.01em;">Customer Record</h3>
                <span class="badge-allowed">{cdata.get('status', 'Active')}</span>
            </div>
            <table style="width:100%; border-collapse:collapse; font-size:0.88rem; color:#f3f4f6;">
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:7px 0; color:#9ca3af; width:35%;">Customer ID</td><td style="padding:7px 0; font-weight:700;">{cdata.get('id')}</td></tr>
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:7px 0; color:#9ca3af;">Name</td><td style="padding:7px 0; font-weight:700;">{cdata.get('name')}</td></tr>
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:7px 0; color:#9ca3af;">Email</td><td style="padding:7px 0; font-weight:600; color:#38bdf8;">{cdata.get('email')}</td></tr>
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:7px 0; color:#9ca3af;">Phone</td><td style="padding:7px 0; font-weight:600;">{cdata.get('phone')}</td></tr>
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:7px 0; color:#9ca3af;">City</td><td style="padding:7px 0;">{cdata.get('city')}</td></tr>
                <tr><td style="padding:7px 0; color:#9ca3af;">Department</td><td style="padding:7px 0; font-weight:600; color:#a855f7;">{cdata.get('department', 'Support')}</td></tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_audit_logs_view():
    """Renders Administrator Dashboard with Audit Timeline, Analytics, and Security Threat Alerts."""
    st.markdown("## **Administrator Governance Console**")
    st.caption("System-wide audit trail, policy decision history, and real-time threat monitoring.")

    logs = []
    try:
        res = requests.get(f"{API_BASE_URL}/audit-logs?limit=100", timeout=4)
        if res.status_code == 200:
            logs = res.json().get("logs", [])
    except Exception:
        pass

    if not logs:
        # Import directly if backend server endpoint is unreachable
        try:
            from backend.logger import audit_logger
            logs = audit_logger.get_logs(limit=100)
        except Exception:
            logs = []

    total_requests = len(logs)
    allowed_count = sum(1 for l in logs if l.get("allowed"))
    blocked_count = total_requests - allowed_count
    active_sessions = len(set(l.get("user") for l in logs if l.get("user")))
    
    # Track probing alerts (>3 blocks per user/agent session)
    user_blocks = {}
    for l in logs:
        if not l.get("allowed"):
            u_key = f"{l.get('user')} ({l.get('agent')})"
            user_blocks[u_key] = user_blocks.get(u_key, 0) + 1

    probing_alerts = [u for u, cnt in user_blocks.items() if cnt >= 3]

    # Top KPI Analytics Cards Bar
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Requests", total_requests)
    m2.metric("Allowed Requests", allowed_count)
    m3.metric("Blocked Requests", blocked_count)
    m4.metric("Permission Violations", blocked_count)
    m5.metric("Active Sessions", active_sessions)

    st.divider()

    # Bonus Feature: Security Alert display ONLY in Administrator Dashboard
    if probing_alerts:
        for alert_user in probing_alerts:
            st.error(
                f"**SECURITY ALERT**: Potential probing behavior detected! "
                f"User/Agent **{alert_user}** has exceeded {user_blocks[alert_user]} failed security checks in this session!"
            )

    st.markdown("### **Audit Timeline Console**")

    if not logs:
        st.info("No audit events recorded in database yet.")
        return

    # Process logs for Administrator table display
    table_data = []
    for l in logs:
        decision_str = "ALLOWED" if l.get("allowed") else "BLOCKED"
        table_data.append({
            "Timestamp": l.get("timestamp"),
            "Session User": l.get("user"),
            "Agent Name": str(l.get("agent")).upper(),
            "Tool Name": "crm",
            "Operation": str(l.get("operation")).upper(),
            "Customer Scope": f"#{l.get('customer_id')}",
            "Decision": decision_str,
            "Reason": l.get("reason")
        })

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )


