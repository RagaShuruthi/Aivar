import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

def render_dashboard_page():
    st.markdown('<div class="gradient-title">📊 Governance SOC Command Center</div>', unsafe_allow_html=True)
    st.caption("Enterprise Observability • Real-Time Policy Decision Point (PDP) Audit Stream & Threat Intelligence")
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

        l_res = requests.get(f"{API_BASE_URL}/audit/logs?limit=100", timeout=3)
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
                    🚨 <b>SECURITY THREAT DETECTED:</b> {alert['reason']} <br/>
                    <small>Timestamp: {alert['timestamp']} | Role: <b>{alert['agent_id']}</b> | Blocked Violations: <b>{alert['total_blocked_count']}</b></small>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Glowing Metric KPI Cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    total_reqs = stats_data.get("total_requests", 0)
    allowed_reqs = stats_data.get("allowed_requests", 0)
    blocked_reqs = stats_data.get("blocked_requests", 0)
    block_rate = stats_data.get("block_rate_percentage", 0.0)
    success_rate = round(100.0 - block_rate, 1) if total_reqs > 0 else 100.0
    active_alerts = stats_data.get("active_alerts_count", 0)

    with c1:
        st.markdown(f'<div class="metric-container"><div class="metric-value">{total_reqs}</div><div class="metric-label">Total Requests</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-container"><div class="metric-value" style="background:linear-gradient(135deg, #10b981 0%, #059669 100%);-webkit-background-clip:text;">{allowed_reqs}</div><div class="metric-label">Allowed Calls</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-container"><div class="metric-value" style="background:linear-gradient(135deg, #ef4444 0%, #dc2626 100%);-webkit-background-clip:text;">{blocked_reqs}</div><div class="metric-label">Blocked Calls</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-container"><div class="metric-value" style="background:linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);-webkit-background-clip:text;">{success_rate}%</div><div class="metric-label">Success Rate</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="metric-container"><div class="metric-value" style="background:linear-gradient(135deg, #a855f7 0%, #7e22ce 100%);-webkit-background-clip:text;">3</div><div class="metric-label">Active Users</div></div>', unsafe_allow_html=True)
    with c6:
        st.markdown(f'<div class="metric-container"><div class="metric-value" style="background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%);-webkit-background-clip:text;">{active_alerts}</div><div class="metric-label">Threat Alerts</div></div>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.divider()

    # Visual SOC Charts Section
    if logs_data:
        df = pd.DataFrame(logs_data)
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("🛡️ Policy Decision Distribution")
            df["Status"] = df["allowed"].apply(lambda x: "Allowed" if x else "Blocked")
            fig_pie = px.pie(
                df,
                names="Status",
                color="Status",
                color_discrete_map={"Allowed": "#10b981", "Blocked": "#ef4444"},
                hole=0.4
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#f3f4f6",
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_right:
            st.subheader("👥 Requests by Enterprise Role")
            role_counts = df["agent_id"].value_counts().reset_index()
            role_counts.columns = ["Role", "Count"]
            fig_bar = px.bar(
                role_counts,
                x="Role",
                y="Count",
                color="Role",
                color_discrete_sequence=["#3b82f6", "#a855f7", "#ef4444"]
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#f3f4f6",
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # Live Audit Activity Stream Table
    st.subheader("⚡ Live Activity Feed (Audit Stream)")
    if logs_data:
        df_logs = pd.DataFrame(logs_data)
        df_logs["Status"] = df_logs["allowed"].apply(lambda x: "✅ ALLOWED" if x else "🚫 BLOCKED")
        display_df = df_logs[["timestamp", "agent_id", "tool_name", "operation", "target_customer_id", "Status", "reason"]]
        display_df.columns = ["Timestamp", "Role", "Tool", "Operation", "Target Customer", "Decision Status", "Policy Reason"]
        st.dataframe(display_df, use_container_width=True, height=360)
    else:
        st.info("No audit activity logged yet. Use the AI CRM Assistant to generate live activity.")
