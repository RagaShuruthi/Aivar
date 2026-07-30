import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime

# 20 Predefined CRM Users matching exact system requirements
PREDEFINED_USERS = {
    101: {"id": 101, "name": "Shruthi", "department": "Support", "role": "support_agent", "role_title": "Support Agent"},
    102: {"id": 102, "name": "Kavin", "department": "Sales", "role": "sales_agent", "role_title": "Sales Agent"},
    103: {"id": 103, "name": "Sabari", "department": "Finance", "role": "support_agent", "role_title": "Support Agent"},
    104: {"id": 104, "name": "Elaki", "department": "HR", "role": "support_agent", "role_title": "Support Agent"},
    105: {"id": 105, "name": "Harini", "department": "Sales", "role": "sales_agent", "role_title": "Sales Agent"},
    106: {"id": 106, "name": "Vignesh", "department": "Support", "role": "support_agent", "role_title": "Support Agent"},
    107: {"id": 107, "name": "Akash", "department": "Sales", "role": "sales_agent", "role_title": "Sales Agent"},
    108: {"id": 108, "name": "Priya", "department": "HR", "role": "support_agent", "role_title": "Support Agent"},
    109: {"id": 109, "name": "Naveen", "department": "Finance", "role": "support_agent", "role_title": "Support Agent"},
    110: {"id": 110, "name": "Keerthana", "department": "Support", "role": "support_agent", "role_title": "Support Agent"},
    111: {"id": 111, "name": "Rahul", "department": "Sales", "role": "sales_agent", "role_title": "Sales Agent"},
    112: {"id": 112, "name": "Nisha", "department": "Support", "role": "support_agent", "role_title": "Support Agent"},
    113: {"id": 113, "name": "Dinesh", "department": "Manager", "role": "sales_agent", "role_title": "Sales Agent"},
    114: {"id": 114, "name": "Kavya", "department": "Support", "role": "support_agent", "role_title": "Support Agent"},
    115: {"id": 115, "name": "Arjun", "department": "Sales", "role": "sales_agent", "role_title": "Sales Agent"},
    116: {"id": 116, "name": "Deepika", "department": "Finance", "role": "support_agent", "role_title": "Support Agent"},
    117: {"id": 117, "name": "Sanjay", "department": "Support", "role": "support_agent", "role_title": "Support Agent"},
    118: {"id": 118, "name": "Meena", "department": "HR", "role": "support_agent", "role_title": "Support Agent"},
    119: {"id": 119, "name": "Ashwin", "department": "Sales", "role": "sales_agent", "role_title": "Sales Agent"},
    120: {"id": 120, "name": "Divya", "department": "Admin", "role": "admin_agent", "role_title": "Admin Agent"},
}

def render_left_sidebar():
    """Renders Left Sidebar with Customer ID User Login & Automatic Agent Resolution."""
    st.sidebar.markdown("## 🛡️ **AI Governance**")
    st.sidebar.caption("Zero-Trust CRM Assistant v2.0")
    st.sidebar.divider()

    st.sidebar.markdown("### 🔑 **Customer ID Login Session**")

    # Select Customer ID (101 to 120)
    user_labels = [f"#{cid} - {info['name']} ({info['role_title']})" for cid, info in PREDEFINED_USERS.items()]
    selected_label = st.sidebar.selectbox(
        "Logged-in Customer ID",
        user_labels,
        index=0,
        key="sidebar_customer_id_select"
    )
    
    selected_cid = int(selected_label.split(" ")[0].replace("#", ""))
    user_info = PREDEFINED_USERS[selected_cid]

    # Store user in session
    st.session_state.active_user = {
        "name": user_info["name"],
        "role": user_info["role"],
        "role_title": user_info["role_title"],
        "customer_id": user_info["id"],
        "department": user_info["department"]
    }
    user = st.session_state.active_user

    st.sidebar.markdown(
        f"""
        <div class="glass-card">
            <div style="font-size:0.8rem; color:#9ca3af;">Session Customer ID:</div>
            <div style="font-weight:bold; font-size:1.15rem; color:#60a5fa;">#{user['customer_id']} - {user['name']}</div>
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
            Validating Agent, Operation, & Customer Scope via <code>manifest.json</code>.
        </div>
        """,
        unsafe_allow_html=True
    )
    return user


def render_execution_trace(last_response: Optional[Dict[str, Any]]):
    """
    Renders Right Sidebar Live Execution Trace Visualizer:
    Gemini Intent -> Selected Agent -> Permission Proxy -> CRM Tool -> Result
    """
    st.markdown("### 🧠 **Execution Trace**")
    st.caption("Live Pipeline Observability & Policy Decision Step-through")
    st.divider()

    if not last_response:
        st.info("💡 Execute a chat query in the center panel to visualize the live execution trace pipeline.")
        return

    intent = last_response.get("intent", {})
    allowed = last_response.get("allowed", False)
    reason = last_response.get("reason", "")
    agent = last_response.get("agent_executed", "support_agent")
    audit_id = last_response.get("audit_log_id", "N/A")

    # Step 1: Gemini Intent Detection
    st.markdown(
        f"""
        <div class="trace-step">
            <div style="font-weight:bold; color:#60a5fa;">1. 🤖 Gemini Intent Detection</div>
            <div style="margin-top:4px; font-family:monospace; color:#cbd5e1;">
                Tool: <b>{str(intent.get('tool', 'crm')).upper()}</b> | Op: <b>{str(intent.get('operation', 'read')).upper()}</b><br/>
                Target Customer: <b>#{intent.get('customer_id', 101)}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Step 2: Agent Dispatcher (Automatic Backend Router)
    st.markdown(
        f"""
        <div class="trace-step">
            <div style="font-weight:bold; color:#a855f7;">2. ⚡ Agent Router (Auto-Selected)</div>
            <div style="margin-top:4px; color:#cbd5e1;">
                Selected Agent: <b>{agent.upper()}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Step 3: Permission Proxy (PDP Scope Check)
    status_badge = '<span class="badge-allowed">✅ ALLOWED</span>' if allowed else '<span class="badge-blocked">🚫 BLOCKED (403)</span>'
    st.markdown(
        f"""
        <div class="trace-step" style="border-left-color: {'#10b981' if allowed else '#ef4444'};">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:bold; color:#f3f4f6;">3. 🛡️ Permission Proxy</span>
                {status_badge}
            </div>
            <div style="margin-top:6px; color:#cbd5e1; font-size:0.8rem;">
                <b>Reason:</b> {reason}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Step 4: CRM Tool Execution
    crm_result_status = "Executed Successfully" if allowed else "Blocked by Proxy (Execution Aborted)"
    st.markdown(
        f"""
        <div class="trace-step">
            <div style="font-weight:bold; color:#f59e0b;">4. 📦 CRM Tool Execution</div>
            <div style="margin-top:4px; color:#cbd5e1;">
                Status: <b>{crm_result_status}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Step 5: Audit Log Metadata
    st.markdown(
        f"""
        <div class="glass-card" style="margin-top:16px;">
            <div style="font-weight:bold; color:#9ca3af; font-size:0.8rem;">AUDIT LOG RECORD</div>
            <div style="font-size:0.85rem; margin-top:4px;">
                Audit Log ID: <code>#LOG-{audit_id}</code><br/>
                Timestamp: <code>{datetime.utcnow().strftime('%H:%M:%S UTC')}</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


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
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:6px 0; color:#9ca3af; width:35%;">Customer ID</td><td style="padding:6px 0; font-weight:bold;">#{cdata.get('id')}</td></tr>
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
