import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

def render_audit_logs_page():
    st.markdown('<div class="gradient-title">📜 Audit Logs Explorer</div>', unsafe_allow_html=True)
    st.markdown("##### *NIST AI RMF Compliant Immutable Request Audit Trail*")
    st.divider()

    # Search & Filter Controls
    f_col1, f_col2, f_col3, f_col4 = st.columns([3, 2, 2, 2])

    with f_col1:
        search_query = st.text_input("🔍 Search Logs (Agent, Reason, Operation)", placeholder="e.g. support_agent or delete")

    with f_col2:
        status_filter = st.selectbox("Status Filter", ["All", "Allowed Only", "Blocked Only"])

    with f_col3:
        agent_filter = st.selectbox("Agent Role", ["All", "support_agent", "admin_agent", "restricted_agent"])

    with f_col4:
        limit_val = st.number_input("Max Records", min_value=10, max_value=1000, value=100)

    # Fetch Logs from Backend
    try:
        allowed_param = None
        if status_filter == "Allowed Only":
            allowed_param = True
        elif status_filter == "Blocked Only":
            allowed_param = False

        agent_param = None if agent_filter == "All" else agent_filter

        query_url = f"{API_BASE_URL}/audit/logs?limit={limit_val}"
        if allowed_param is not None:
            query_url += f"&allowed={'true' if allowed_param else 'false'}"
        if agent_param:
            query_url += f"&agent_id={agent_param}"

        res = requests.get(query_url, timeout=3)
        if res.status_code == 200:
            logs = res.json().get("logs", [])
        else:
            logs = []
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        logs = []

    if logs:
        df = pd.DataFrame(logs)

        # Apply search filter
        if search_query:
            sq = search_query.lower()
            df = df[
                df["agent_id"].str.lower().str.contains(sq) |
                df["reason"].str.lower().str.contains(sq) |
                df["operation"].str.lower().str.contains(sq)
            ]

        st.markdown(f"**Showing {len(df)} audit records:**")

        # Download CSV Button
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Export Audit Trail CSV",
            data=csv_data,
            file_name="audit_logs_export.csv",
            mime="text/csv"
        )

        df["Status"] = df["allowed"].apply(lambda x: "✅ ALLOWED" if x else "🚫 BLOCKED")
        display_df = df[["id", "timestamp", "agent_id", "tool_name", "operation", "target_customer_id", "Status", "reason"]]
        display_df.columns = ["Log ID", "Timestamp", "Agent Role", "Tool", "Operation", "Target Customer ID", "Status", "Decision Reasoning"]

        st.dataframe(display_df, use_container_width=True, height=500)
    else:
        st.info("No matching audit log records found.")
