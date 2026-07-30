import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime

def render_left_sidebar():
    """Renders Left Sidebar with Current User, Role, Active Agent, and Status."""
    st.sidebar.markdown("## 🛡️ **AI Governance**")
    st.sidebar.caption("Zero-Trust CRM Assistant v2.0")
    st.sidebar.divider()

    st.sidebar.markdown("### 👤 **Current User Session**")
    
    # Pre-configured user options
    user_options = {
        "Alice Smith (Support Agent)": {"name": "Alice Smith", "role": "support_agent", "role_title": "Support Agent", "customer_id": 101},
        "Bob Jones (Sales Agent)": {"name": "Bob Jones", "role": "sales_agent", "role_title": "Sales Agent", "customer_id": 105},
        "Shuruthi (Admin Agent)": {"name": "Shuruthi", "role": "admin_agent", "role_title": "Admin Agent", "customer_id": 101},
    }

    selected_user_key = st.sidebar.selectbox(
        "Switch Demo User / Role",
        list(user_options.keys()),
        index=0,
        key="left_sidebar_user_select"
    )
    user = user_options[selected_user_key]

    st.session_state.active_user = user

    st.sidebar.markdown(
        f"""
        <div class="glass-card">
            <div style="font-size:0.85rem; color:#9ca3af;">Authenticated User:</div>
            <div style="font-weight:bold; font-size:1.05rem; color:#f3f4f6;">{user['name']}</div>
            <div style="font-size:0.85rem; color:#60a5fa; font-weight:600; margin-top:4px;">Role: {user['role_title']}</div>
            <div style="font-size:0.75rem; color:#9ca3af; margin-top:2px;">Session CID: <b>#{user['customer_id']}</b></div>
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
            Enforcing dynamic rules from <code>manifest.json</code>. Direct CRM access is <b>DISABLED</b>.
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

    # Step 2: Agent Dispatcher
    st.markdown(
        f"""
        <div class="trace-step">
            <div style="font-weight:bold; color:#a855f7;">2. ⚡ Agent Dispatcher</div>
            <div style="margin-top:4px; color:#cbd5e1;">
                Dispatched to: <b>{agent.upper()}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Step 3: Permission Proxy (PDP)
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
                <h3 style="margin:0; color:#10b981; font-size:1.1rem; font-weight:700;">Customer Information Card</h3>
                <span class="badge-allowed">{cdata.get('status', 'Active')}</span>
            </div>
            <table style="width:100%; border-collapse:collapse; font-size:0.9rem; color:#f3f4f6;">
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:6px 0; color:#9ca3af; width:35%;">Customer ID</td><td style="padding:6px 0; font-weight:bold;">#{cdata.get('id')}</td></tr>
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:6px 0; color:#9ca3af;">Name</td><td style="padding:6px 0; font-weight:bold;">{cdata.get('name')}</td></tr>
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:6px 0; color:#9ca3af;">Email</td><td style="padding:6px 0; font-weight:bold; color:#38bdf8;">{cdata.get('email')}</td></tr>
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:6px 0; color:#9ca3af;">Phone</td><td style="padding:6px 0; font-weight:bold;">{cdata.get('phone')}</td></tr>
                <tr style="border-bottom:1px solid #1f2937;"><td style="padding:6px 0; color:#9ca3af;">City</td><td style="padding:6px 0;">{cdata.get('city')}</td></tr>
                <tr><td style="padding:6px 0; color:#9ca3af;">Company</td><td style="padding:6px 0; font-weight:bold; color:#a855f7;">{cdata.get('company')}</td></tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )
