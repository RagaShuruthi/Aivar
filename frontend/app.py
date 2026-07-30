import streamlit as st
import requests
from frontend.theme import apply_production_theme
from frontend.components import render_left_sidebar, render_execution_trace, render_customer_card

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# Page Configuration
st.set_page_config(
    page_title="Agentic AI CRM Assistant with Permission Proxy",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Theme
apply_production_theme()

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_pipeline_response" not in st.session_state:
    st.session_state.last_pipeline_response = None

# Render Left Sidebar User Controls & Permission Status
active_user = render_left_sidebar()

# Main 2-Column Layout (Center Chat + Right Sidebar Trace Visualizer)
col_chat, col_trace = st.columns([2, 1])

# --- CENTER COLUMN: CHAT INTERFACE ---
with col_chat:
    st.markdown('<div class="main-title">🛡️ Agentic AI CRM Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Zero-Trust CRM Automation Powered by Permission Proxy & Gemini 2.5 Flash</div>', unsafe_allow_html=True)

    # Quick Test Chips Bar
    st.markdown("**⚡ Try Sample Natural Language Commands:**")
    q1, q2, q3, q4 = st.columns(4)
    prompt_to_send = None

    if q1.button("👤 Show customer 101", use_container_width=True, key="btn_sample_101"):
        prompt_to_send = "Show customer 101."
    if q2.button("✏️ Update 105 phone", use_container_width=True, key="btn_sample_phone"):
        prompt_to_send = "Update customer 105 phone number to 9876543210."
    if q3.button("❌ Delete customer 102", use_container_width=True, key="btn_sample_delete"):
        prompt_to_send = "Delete customer 102."
    if q4.button("🔍 Show all customers", use_container_width=True, key="btn_sample_list"):
        prompt_to_send = "Show customer 103 profile."

    st.markdown("<br/>", unsafe_allow_html=True)

    # Chat Scrollable Container
    chat_container = st.container(height=520)
    with chat_container:
        if not st.session_state.messages:
            st.markdown(
                '<div style="text-align:center; color:#9ca3af; padding:60px 20px;">'
                '💬 Type a natural language request below.<br/>'
                'Example: <i>"Show customer 101"</i>, <i>"Update customer 105 phone to 9876543210"</i>, or <i>"Delete customer 102"</i>.'
                '</div>',
                unsafe_allow_html=True
            )

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-bubble">👤 <b>{msg["text"]}</b></div>', unsafe_allow_html=True)
            elif msg["role"] == "assistant":
                allowed = msg.get("allowed", False)
                reason = msg.get("reason", "")
                resp_text = msg.get("response_text", "")
                cdata = msg.get("data")

                st.markdown(
                    f"""
                    <div class="ai-bubble">
                        <div style="font-weight:bold; color:#60a5fa; margin-bottom:6px;">🤖 AI CRM Assistant</div>
                        <div>{resp_text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # If allowed and customer profile returned, render structured card
                if allowed and isinstance(cdata, dict) and "id" in cdata:
                    render_customer_card(cdata)

    # Chat Input Box
    user_input = st.chat_input("Type your CRM command (e.g., 'Show customer 101', 'Delete customer 102')...", key="chat_input_main")
    if user_input:
        prompt_to_send = user_input

    # Send Pipeline Request
    if prompt_to_send:
        st.session_state.messages.append({"role": "user", "text": prompt_to_send})

        payload = {
            "user": active_user["name"],
            "agent_role": active_user["role"],
            "prompt": prompt_to_send,
            "session_customer_id": active_user["customer_id"]
        }

        try:
            res = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=10)
            if res.status_code == 200:
                pipeline_res = res.json()
            else:
                pipeline_res = {
                    "allowed": False,
                    "reason": f"API Error {res.status_code}: {res.text}",
                    "response_text": f"🚫 Error communicating with backend: {res.text}",
                    "intent": {"tool": "crm", "operation": "unknown", "customer_id": active_user["customer_id"]},
                    "agent_executed": active_user["role"],
                    "audit_log_id": 0,
                    "data": None
                }
        except Exception as e:
            pipeline_res = {
                "allowed": False,
                "reason": f"Backend API Connection Error: {str(e)}",
                "response_text": f"🚫 Backend Connection Failed: Please ensure FastAPI is running on port 8000.",
                "intent": {"tool": "crm", "operation": "unknown", "customer_id": active_user["customer_id"]},
                "agent_executed": active_user["role"],
                "audit_log_id": 0,
                "data": None
            }

        st.session_state.last_pipeline_response = pipeline_res

        st.session_state.messages.append({
            "role": "assistant",
            "allowed": pipeline_res["allowed"],
            "reason": pipeline_res["reason"],
            "response_text": pipeline_res["response_text"],
            "data": pipeline_res.get("data")
        })

        st.rerun()

# --- RIGHT COLUMN: EXECUTION TRACE VISUALIZER ---
with col_trace:
    render_execution_trace(st.session_state.last_pipeline_response)
