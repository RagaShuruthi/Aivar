import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

def render_dashboard_page():
    st.markdown('<div class="gradient-title">📊 Governance & Security Dashboard</div>', unsafe_allow_html=True)
    st.markdown("##### *Real-Time SOC Command Center & Threat Observability*")
    st.divider()

    # Fetch Metrics & Active Alerts
    stats_data = {"total_requests": 0, "allowed_requests": 0, "blocked_requests": 0, "block_rate_percentage": 0.0, "active_alerts_count": 0}
    alerts_data = []
    logs_data = []

    try:
        s_res = requests.get(f"{API_BASE_URL}/audit/stats", timeout=3)
        if s_res.status_code == 200:
            stats_data = s_res.json()

        a_res = requests.get(f"{API_BASE_URL}/audit/alerts?active_only=true", timeout=3)
        if a_res.status_code == 200:
            alerts_data = a_res.json().get("alerts", [])

        l_res = requests.get(f"{API_BASE_URL}/audit/logs?limit=50", timeout=3)
        if l_res.status_code == 200:
            logs_data = l_res.json().get("logs", [])
    except Exception:
        st.error("⚠️ Backend API server offline. Start server via: `python run_all.py`")

    # Render Active Threat Banners (>3 Blocked Requests)
    if alerts_data:
        for alert in alerts_data:
            st.markdown(
                f"""
                <div class="threat-alert-box">
                    🚨 <b>SECURITY THREAT THRESHOLD BREACHED:</b> {alert['reason']} <br/>
                    <small>Detected Timestamp: {alert['timestamp']} | Compromised Agent: <b>{alert['agent_id']}</b> | Total Blocked Violations: <b>{alert['total_blocked_count']}</b></small>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Glowing Metric KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="metric-container"><div class="metric-value">{stats_data.get("total_requests", 0)}</div><div class="metric-label">Total Tool Calls</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-container"><div class="metric-value" style="background:linear-gradient(135deg, #10b981 0%, #059669 100%);-webkit-background-clip:text;">{stats_data.get("allowed_requests", 0)}</div><div class="metric-label">Allowed Calls</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-container"><div class="metric-value" style="background:linear-gradient(135deg, #ef4444 0%, #dc2626 100%);-webkit-background-clip:text;">{stats_data.get("blocked_requests", 0)}</div><div class="metric-label">Blocked Calls</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-container"><div class="metric-value">{stats_data.get("block_rate_percentage", 0.0)}%</div><div class="metric-label">Block Rate</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-container"><div class="metric-value" style="background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%);-webkit-background-clip:text;">{stats_data.get("active_alerts_count", 0)}</div><div class="metric-label">Active Alerts</div></div>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.divider()

    # Recent Audit Log Activity Stream
    st.subheader("⚡ Live Audit Activity Stream")
    if logs_data:
        df = pd.DataFrame(logs_data)
        df["Status"] = df["allowed"].apply(lambda x: "✅ ALLOWED" if x else "🚫 BLOCKED")
        display_df = df[["timestamp", "agent_id", "tool_name", "operation", "target_customer_id", "Status", "reason"]]
        display_df.columns = ["Timestamp", "Agent ID", "Tool", "Operation", "Target Customer ID", "Status", "Reasoning"]
        st.dataframe(display_df, use_container_width=True, height=380)
    else:
        st.info("No audit logs recorded yet. Interact with the AI Assistant to generate activity.")
