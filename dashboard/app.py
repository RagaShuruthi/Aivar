import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Backend API Configuration
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# Configure Page Layout and Theme
st.set_page_config(
    page_title="AI Governance - Tool Permission Enforcer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium SOC Aesthetics
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .metric-card {
        background-color: #1e222d;
        border: 1px solid #2e364f;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .status-allowed {
        color: #00e676;
        font-weight: bold;
    }
    .status-blocked {
        color: #ff5252;
        font-weight: bold;
    }
    .alert-banner {
        background: linear-gradient(90deg, #ff1744 0%, #b00020 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Application Header
st.title("🛡️ AI Governance: Tool Permission Enforcer")
st.caption("Production-Ready Zero-Trust Proxy & Real-Time Audit Monitoring System (PS-2.2)")

st.divider()

# Sidebar: Interactive AI Agent Test Simulator
st.sidebar.header("🧪 AI Agent Simulator")
st.sidebar.markdown("Simulate AI Agent tool requests to test real-time policy enforcement.")

# Database Seed Trigger Button
if st.sidebar.button("🌱 Seed CRM Database (IDs 101, 102, 103)"):
    try:
        res = requests.post(f"{API_BASE_URL}/crm/seed")
        if res.status_code == 201:
            st.sidebar.success("Database seeded with sample customer data!")
        else:
            st.sidebar.info("Database already contains customer data.")
    except Exception as e:
        st.sidebar.error(f"Backend Connection Error: {e}")

st.sidebar.divider()

# Form controls for Agent Simulator
selected_agent = st.sidebar.selectbox(
    "Select Agent Role",
    ["support_agent", "admin_agent", "restricted_agent"],
    help="support_agent: Read-only (session customer)\nadmin_agent: Full CRUD (global)\nrestricted_agent: Blocked"
)

selected_operation = st.sidebar.selectbox(
    "Select Tool Operation",
    ["read", "update", "delete"]
)

target_customer_id = st.sidebar.number_input("Target Customer ID", min_value=100, max_value=999, value=101)
session_customer_id = st.sidebar.number_input("Session Context Customer ID", min_value=100, max_value=999, value=101)

# Optional payload data for update operations
update_name = ""
if selected_operation == "update":
    update_name = st.sidebar.text_input("New Customer Name", value="Alice Smith (Updated)")

# Trigger Tool Call Execution
if st.sidebar.button("🚀 Invoke Tool Request", type="primary"):
    payload = {
        "agent_id": selected_agent,
        "tool_name": "crm",
        "operation": selected_operation,
        "target_customer_id": target_customer_id,
        "session_context": {
            "customer_id": session_customer_id
        }
    }
    if selected_operation == "update" and update_name:
        payload["payload_data"] = {"name": update_name}

    try:
        response = requests.post(f"{API_BASE_URL}/proxy/invoke-tool", json=payload)
        if response.status_code == 200:
            res_data = response.json()
            st.sidebar.success(f"✅ ALLOWED: {res_data['permission_decision']['reason']}")
            st.sidebar.json(res_data["data"])
        elif response.status_code == 403:
            err_data = response.json()["detail"]
            st.sidebar.error(f"🚫 BLOCKED (403 Forbidden): {err_data['reason']}")
        else:
            st.sidebar.warning(f"Response ({response.status_code}): {response.text}")
    except Exception as e:
        st.sidebar.error(f"Proxy Connection Error: Make sure FastAPI is running on port 8000! Details: {e}")

# Fetch Stats & Alerts from API
stats_data = {"total_requests": 0, "allowed_requests": 0, "blocked_requests": 0, "block_rate_percentage": 0.0, "active_alerts_count": 0}
alerts_data = []
logs_data = []

try:
    s_res = requests.get(f"{API_BASE_URL}/audit/stats")
    if s_res.status_code == 200:
        stats_data = s_res.json()

    a_res = requests.get(f"{API_BASE_URL}/audit/alerts?active_only=true")
    if a_res.status_code == 200:
        alerts_data = a_res.json().get("alerts", [])

    l_res = requests.get(f"{API_BASE_URL}/audit/logs?limit=100")
    if l_res.status_code == 200:
        logs_data = l_res.json().get("logs", [])
except Exception:
    st.warning("⚠️ Backend API server unreachable. Please start FastAPI using: `uvicorn app.main:app --reload`")

# Render Active Threat Banners (Bonus Requirement: >3 Blocked Attempts Alert)
if alerts_data:
    for alert in alerts_data:
        st.markdown(
            f"""
            <div class="alert-banner">
                🚨 <b>SECURITY THREAT DETECTED:</b> {alert['reason']} <br/>
                <small>Timestamp: {alert['timestamp']} | Agent: <b>{alert['agent_id']}</b> | Blocked Violations: <b>{alert['total_blocked_count']}</b></small>
            </div>
            """,
            unsafe_allow_html=True
        )

# KPI Governance Metrics Cards
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Tool Calls", stats_data.get("total_requests", 0))
with col2:
    st.metric("Allowed Calls", stats_data.get("allowed_requests", 0))
with col3:
    st.metric("Blocked Calls", stats_data.get("blocked_requests", 0))
with col4:
    st.metric("Block Rate", f"{stats_data.get('block_rate_percentage', 0.0)}%")
with col5:
    st.metric("Security Alerts", stats_data.get("active_alerts_count", 0))

st.divider()

# Tab Navigation: Audit Logs & Security Threat Panel
tab1, tab2 = st.tabs(["📜 Real-Time Audit Trail", "⚠️ Security Threat Log"])

with tab1:
    st.subheader("Audit Logs Explorer")
    filter_option = st.radio("Filter Status:", ["All", "Allowed Only", "Blocked Only"], horizontal=True)

    if logs_data:
        df = pd.DataFrame(logs_data)
        if filter_option == "Allowed Only":
            df = df[df["allowed"] == True]
        elif filter_option == "Blocked Only":
            df = df[df["allowed"] == False]

        # Format dataframe for display
        df["Status"] = df["allowed"].apply(lambda x: "✅ ALLOWED" if x else "🚫 BLOCKED")
        display_df = df[["timestamp", "agent_id", "tool_name", "operation", "target_customer_id", "Status", "reason"]]
        display_df.columns = ["Timestamp", "Agent ID", "Tool", "Operation", "Target Customer ID", "Status", "Reasoning"]

        st.dataframe(display_df, use_container_width=True, height=400)
    else:
        st.info("No audit logs recorded yet. Use the AI Agent Simulator on the sidebar to send requests!")

with tab2:
    st.subheader("Active & Historical Security Alerts")
    try:
        all_alerts_res = requests.get(f"{API_BASE_URL}/audit/alerts")
        if all_alerts_res.status_code == 200:
            all_alerts = all_alerts_res.json().get("alerts", [])
            if all_alerts:
                adf = pd.DataFrame(all_alerts)
                adf.columns = ["Alert ID", "Timestamp", "Agent ID", "Violation Details", "Total Blocked Actions", "Active Status"]
                st.dataframe(adf, use_container_width=True)
            else:
                st.success("No security threshold breaches detected.")
    except Exception as e:
        st.error(f"Error loading alerts: {e}")
