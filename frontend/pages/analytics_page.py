import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

def render_analytics_page():
    st.markdown('<div class="gradient-title">📈 Agent Analytics & Threat Intelligence</div>', unsafe_allow_html=True)
    st.markdown("##### *Behavioral Risk Profiling, Operation Breakdown & Security Violation Trends*")
    st.divider()

    try:
        l_res = requests.get(f"{API_BASE_URL}/audit/logs?limit=1000", timeout=3)
        a_res = requests.get(f"{API_BASE_URL}/audit/alerts", timeout=3)

        logs = l_res.json().get("logs", []) if l_res.status_code == 200 else []
        alerts = a_res.json().get("alerts", []) if a_res.status_code == 200 else []
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        logs, alerts = [], []

    if not logs:
        st.info("Insufficient data for analytics. Interact with the AI Assistant to generate activity logs.")
        return

    df = pd.DataFrame(logs)

    # Plotly Section 1: Allowed vs Blocked by Agent Role
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("📊 Enforcement Outcome by Agent Role")
        role_status = df.groupby(["agent_id", "allowed"]).size().reset_index(name="count")
        role_status["Status"] = role_status["allowed"].apply(lambda x: "Allowed" if x else "Blocked")

        fig1 = px.bar(
            role_status,
            x="agent_id",
            y="count",
            color="Status",
            barmode="group",
            color_discrete_map={"Allowed": "#10b981", "Blocked": "#ef4444"},
            labels={"agent_id": "Agent Role", "count": "Total Tool Calls"},
            template="plotly_dark"
        )
        fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        st.subheader("🍕 Tool Operation Distribution")
        op_counts = df.groupby("operation").size().reset_index(name="count")
        fig2 = px.pie(
            op_counts,
            names="operation",
            values="count",
            color="operation",
            color_discrete_map={"read": "#38bdf8", "update": "#a855f7", "delete": "#f43f5e"},
            hole=0.4,
            template="plotly_dark"
        )
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Threat Alerts Log Section
    st.subheader("🚨 Security Threshold Violation Breaches (>3 Blocked Actions)")
    if alerts:
        adf = pd.DataFrame(alerts)
        adf["Active Status"] = adf["is_active"].apply(lambda x: "🔴 ACTIVE THREAT" if x else "⚪ RESOLVED")
        display_adf = adf[["timestamp", "agent_id", "total_blocked_count", "Active Status", "reason"]]
        display_adf.columns = ["Detected Time", "Compromised Agent", "Blocked Count", "Threat Status", "Alert Reason"]
        st.dataframe(display_adf, use_container_width=True)
    else:
        st.success("Zero security threshold breaches recorded. System operating securely.")
