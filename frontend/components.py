import streamlit as st
import requests
from typing import Dict, Any, Optional
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# 20 Predefined CRM Users matching exact system requirements
PREDEFINED_USERS = {
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

def render_left_sidebar():
    """Renders Left Sidebar with Logged-In User Profile Badge & Permission Proxy Status."""
    st.sidebar.markdown("## 🛡️ **AI Governance**")
    st.sidebar.caption("Zero-Trust CRM Assistant v2.0")
    st.sidebar.divider()

    # Retrieve logged-in user from session state
    user = st.session_state.get("user")
    if not user:
        user = PREDEFINED_USERS[101]

    st.sidebar.markdown("### 👤 **Logged-in Session Profile**")
    st.sidebar.markdown(
        f"""
        <div class="glass-card">
            <div style="font-size:0.8rem; color:#9ca3af;">Session Customer ID:</div>
            <div style="font-weight:bold; font-size:1.2rem; color:#60a5fa;">ID: {user['customer_id']} - {user['name']}</div>
            <div style="font-size:0.85rem; color:#a855f7; font-weight:600; margin-top:4px;">Department: {user['department']}</div>
            <div style="font-size:0.85rem; color:#10b981; font-weight:600; margin-top:2px;">Auto AI Agent: <b>{user['role_title']}</b></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.divider()
    st.sidebar.markdown("### 🔒 **Permission Proxy Status**")
    st.sidebar.markdown(
        """
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:10px; height:10px; border-radius:50%; background:#10b981; box-shadow: 0 0 10px #10b981;"></div>
            <span style="font-weight:bold; color:#10b981; font-size:0.9rem;">Policy Gateway ACTIVE</span>
        </div>
        <div style="font-size:0.75rem; color:#9ca3af; margin-top:6px;">
            Enforcing Zero-Trust scope validation via <code>manifest.json</code>.
        </div>
        """,
        unsafe_allow_html=True
    )
    return user


def render_customer_card(cdata: Dict[str, Any]):
    """Renders modern Customer Profile Card when allowed."""
    st.markdown(
        f"""
        <div class="glass-card" style="border:1px solid #10b981;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <h3 style="margin:0; color:#10b981; font-size:1.1rem; font-weight:700;">Customer Record</h3>
                <span class="badge-allowed">{cdata.get('status', 'Active')}</span>
            </div>
            <table style="width:100%; border-collapse:collapse; font-size:0.9rem; color:#f3f4f6;">
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:6px 0; color:#9ca3af; width:35%;">Customer ID</td><td style="padding:6px 0; font-weight:bold;">{cdata.get('id')}</td></tr>
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:6px 0; color:#9ca3af;">Name</td><td style="padding:6px 0; font-weight:bold;">{cdata.get('name')}</td></tr>
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:6px 0; color:#9ca3af;">Email</td><td style="padding:6px 0; font-weight:bold; color:#38bdf8;">{cdata.get('email')}</td></tr>
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:6px 0; color:#9ca3af;">Phone</td><td style="padding:6px 0; font-weight:bold;">{cdata.get('phone')}</td></tr>
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:6px 0; color:#9ca3af;">City</td><td style="padding:6px 0;">{cdata.get('city')}</td></tr>
                <tr><td style="padding:6px 0; color:#9ca3af;">Department</td><td style="padding:6px 0; font-weight:bold; color:#a855f7;">{cdata.get('department', 'Support')}</td></tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_audit_logs_view():
    """Renders real-time time-based audit log trail and security metrics."""
    st.markdown("## 📜 **Audit Trail & Governance Command Center**")
    st.caption("Real-time time-based log feed tracking every Permission Proxy decision.")

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
    threat_alerts = sum(1 for l in logs if "SECURITY ALERT" in l.get("reason", ""))

    # Top KPI Stats Bar
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Tool Requests", total_requests)
    m2.metric("✅ Allowed Operations", allowed_count)
    m3.metric("🚫 Blocked Violations", blocked_count)
    m4.metric("🚨 Probing Alerts", threat_alerts)

    st.divider()

    if threat_alerts > 0:
        st.warning(f"🚨 **Security Warning**: Detected {threat_alerts} probing threat alert(s) exceeding 3+ out-of-scope/policy violations per session!")

    st.markdown("### 🕒 **Live Time-based Log Feed**")

    if not logs:
        st.info("No audit logs recorded yet. Send queries in the AI CRM Assistant tab to populate the audit stream.")
        return

    # Process logs for display table
    table_data = []
    for l in logs:
        status_str = "✅ ALLOWED" if l.get("allowed") else "🚫 BLOCKED (403)"
        table_data.append({
            "Log ID": f"LOG-{l.get('id')}",
            "Timestamp (UTC)": l.get("timestamp"),
            "User": l.get("user"),
            "Agent": str(l.get("agent")).upper(),
            "Operation": str(l.get("operation")).upper(),
            "Customer ID": str(l.get("customer_id")),
            "Status": status_str,
            "Reason / Policy Decision": l.get("reason")
        })

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )
