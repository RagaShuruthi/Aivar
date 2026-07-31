import streamlit as st
from frontend.theme import apply_production_theme
from frontend.components import render_audit_logs_view

# Configure Page Layout and Theme
st.set_page_config(
    page_title="Administrator Dashboard - CRM Security Console",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Theme
apply_production_theme()

st.sidebar.markdown("## **Administrator Console**")
st.sidebar.caption("System Governance & Audit Engine")
st.sidebar.divider()

st.sidebar.info("You are viewing the dedicated **Administrator Dashboard**. Access is restricted to system administrators.")

# Render Administrator Dashboard
render_audit_logs_view()

