import streamlit as st
import requests
from frontend.theme import apply_production_theme
from frontend.components import render_left_sidebar, render_customer_card, render_audit_logs_view
from frontend.views.login import render_login_page, auto_login_from_query_params

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# Page Configuration
st.set_page_config(
    page_title="Enterprise CRM Security Portal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Theme
apply_production_theme()

# Auto-restore session from query params if available
auto_login_from_query_params()

# Check Authentication State
if not st.session_state.get("authenticated", False):
    # Render Login Page FIRST
    render_login_page()
    st.stop()

# Session State Initialization for Chat & Multi-turn Pending Update
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_update" not in st.session_state:
    st.session_state.pending_update = None

# Render Left Sidebar User Controls & Permission Status
active_user = render_left_sidebar()

st.sidebar.divider()

# Interface Mode Selection (User Portal vs Administrator Dashboard)
interface_mode = st.sidebar.radio(
    "Select Interface",
    ["User Portal (AI Chat)", "Administrator Dashboard"],
    index=0,
    key="nav_interface_mode"
)

st.sidebar.divider()

if st.sidebar.button("Clear Chat History", use_container_width=True, key="sidebar_clear_history_btn"):
    st.session_state.messages = []
    st.session_state.pending_update = None
    st.rerun()

if st.sidebar.button("Re-initialize Session Context", use_container_width=True, key="sidebar_reinit_btn"):
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.messages = []
    st.session_state.pending_update = None
    st.query_params.clear()
    st.rerun()

# --- INTERFACE 1: USER PORTAL (AI CHAT ASSISTANT ONLY) ---
if interface_mode == "User Portal (AI Chat)":
    st.markdown('<div class="main-title">User Portal</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="subtitle">Session User: <b>{active_user["name"]}</b> | User Role: <b>{active_user["role_title"]}</b> | Session Customer Scope: <b>#{active_user["customer_id"]}</b></div>',
        unsafe_allow_html=True
    )


    # Quick Action Chips
    st.markdown("**Sample Actions:**")
    q1, q2, q3, q4 = st.columns(4)
    prompt_to_send = None

    if q1.button(f"View My Profile (#{active_user['customer_id']})", use_container_width=True, key="btn_sample_own"):
        prompt_to_send = f"Show customer {active_user['customer_id']} profile."
    if q2.button("Update Customer Phone", use_container_width=True, key="btn_sample_update"):
        prompt_to_send = f"Update customer {active_user['customer_id']} phone number to +1-555-9876."
    if q3.button("What Was Updated?", use_container_width=True, key="btn_sample_audit"):
        prompt_to_send = "What was updated recently?"
    if q4.button("Delete Customer 102", use_container_width=True, key="btn_sample_delete"):
        prompt_to_send = "Delete customer 102."

    st.markdown("<br/>", unsafe_allow_html=True)

    # Chat Scrollable Container (Clean AI Chat Interface ONLY - No raw logs or internal tool calls)
    chat_container = st.container(height=480)
    with chat_container:
        if not st.session_state.messages:
            st.markdown(
                '<div style="text-align:center; color:#9ca3af; padding:80px 20px;">'
                '<h3 style="color:#f3f4f6; margin-bottom:8px; font-weight:700;">AI CRM Chat Assistant</h3>'
                '<span style="font-size:0.9rem;">Ask a question or issue a customer record command.<br/>'
                'Examples: <i>"Show customer 101"</i>, <i>"Update customer 105 phone"</i>, <i>"What was updated?"</i></span>'
                '</div>',
                unsafe_allow_html=True
            )

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-bubble"><b>{msg["text"]}</b></div>', unsafe_allow_html=True)
            elif msg["role"] == "assistant":
                allowed = msg.get("allowed", False)
                resp_text = msg.get("response_text", "")
                cdata = msg.get("data")

                st.markdown(
                    f"""
                    <div class="ai-bubble">
                        <div style="font-weight:700; color:#60a5fa; margin-bottom:6px; font-size:0.9rem;">CRM Assistant</div>
                        <div>{resp_text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Render Customer Card if returned
                if allowed and isinstance(cdata, dict) and "id" in cdata:
                    render_customer_card(cdata)

    # Chat Input Box
    user_input = st.chat_input("Type your message...", key="chat_input_main")
    if user_input:
        prompt_to_send = user_input

    # Send Pipeline Request with Multi-turn Update Follow-up Handling
    if prompt_to_send:
        # Check if we are in a pending multi-turn update conversation
        if st.session_state.pending_update is not None:
            pu = st.session_state.pending_update
            st.session_state.messages.append({"role": "user", "text": prompt_to_send})
            
            if pu["step"] == "customer_id":
                # User provided customer ID
                import re
                cid_match = re.search(r'\b(\d{3})\b', prompt_to_send)
                if cid_match:
                    pu["customer_id"] = int(cid_match.group(1))
                    if not pu.get("field"):
                        pu["step"] = "field"
                        reply = f"Which field for customer #{pu['customer_id']} would you like to update? (Options: phone, email, name, city, status)"
                    elif not pu.get("value"):
                        pu["step"] = "value"
                        reply = f"What should the new value for {pu['field']} be?"
                    else:
                        pu["step"] = "complete"
                else:
                    reply = "Please specify a valid 3-digit Customer ID (e.g. 101, 105)."

                if pu["step"] != "complete":
                    st.session_state.messages.append({
                        "role": "assistant",
                        "allowed": True,
                        "response_text": reply
                    })
                    st.rerun()

            elif pu["step"] == "field":
                # User provided field
                prompt_low = prompt_to_send.lower()
                matched_field = None
                for f in ["phone", "email", "name", "city", "status"]:
                    if f in prompt_low:
                        matched_field = f
                        break
                if matched_field:
                    pu["field"] = matched_field
                    if not pu.get("value"):
                        pu["step"] = "value"
                        reply = f"What should the new value for {pu['field']} be?"
                    else:
                        pu["step"] = "complete"
                else:
                    reply = "Which field would you like to update? Please select from: phone, email, name, city, status."

                if pu["step"] != "complete":
                    st.session_state.messages.append({
                        "role": "assistant",
                        "allowed": True,
                        "response_text": reply
                    })
                    st.rerun()

            elif pu["step"] == "value":
                # User provided new value
                pu["value"] = prompt_to_send.strip()
                pu["step"] = "complete"

            # If all update info collected, execute update via Permission Proxy!
            if pu["step"] == "complete":
                final_prompt = f"Update customer {pu['customer_id']} {pu['field']} to {pu['value']}"
                st.session_state.pending_update = None
                prompt_to_send = final_prompt

        # Normal query processing
        if prompt_to_send and st.session_state.pending_update is None:
            # Check if this is an incomplete update prompt that needs follow-up
            prompt_low = prompt_to_send.lower()
            if any(w in prompt_low for w in ["update customer", "update", "updation", "modify"]) and not any(w in prompt_low for w in ["what was updated", "show history"]):
                import re
                has_cid = re.search(r'\b(\d{3})\b', prompt_low)
                has_field = any(f in prompt_low for f in ["phone", "email", "name", "city", "status"])
                has_val = False
                if has_field:
                    if "phone" in prompt_low and re.search(r'\b(\+?\d[-0-9\s]{7,15})\b', prompt_to_send):
                        has_val = True
                    elif "email" in prompt_low and "@" in prompt_to_send:
                        has_val = True
                    elif ("city" in prompt_low or "name" in prompt_low) and (" to " in prompt_low or " is " in prompt_low or "=" in prompt_low):
                        has_val = True

                if not (has_cid and has_field and has_val):
                    # Information missing! Start follow-up sequence
                    st.session_state.messages.append({"role": "user", "text": prompt_to_send})
                    cid = int(has_cid.group(1)) if has_cid else None
                    fld = "phone" if "phone" in prompt_low else ("email" if "email" in prompt_low else ("city" if "city" in prompt_low else None))
                    val = None

                    if not cid:
                        st.session_state.pending_update = {"step": "customer_id", "customer_id": None, "field": fld, "value": val}
                        st.session_state.messages.append({
                            "role": "assistant",
                            "allowed": True,
                            "response_text": "Which customer would you like to update? (Please specify customer ID, e.g. 101, 105)"
                        })
                        st.rerun()
                    elif not fld:
                        st.session_state.pending_update = {"step": "field", "customer_id": cid, "field": None, "value": val}
                        st.session_state.messages.append({
                            "role": "assistant",
                            "allowed": True,
                            "response_text": f"Which field for customer #{cid} would you like to update? (Options: phone, email, name, city, status)"
                        })
                        st.rerun()
                    elif not has_val:
                        st.session_state.pending_update = {"step": "value", "customer_id": cid, "field": fld, "value": None}
                        st.session_state.messages.append({
                            "role": "assistant",
                            "allowed": True,
                            "response_text": f"What should the new value for {fld} be?"
                        })
                        st.rerun()

            # Normal request execution via Permission Proxy
            st.session_state.messages.append({"role": "user", "text": prompt_to_send})

            payload = {
                "user": active_user["name"],
                "user_role": active_user["role"],
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
                        "response_text": f"Error communicating with backend API.",
                        "data": None
                    }
            except Exception as e:
                pipeline_res = {
                    "allowed": False,
                    "reason": f"Backend Connection Error: {str(e)}",
                    "response_text": "Backend Connection Failed: Ensure FastAPI is running on port 8000.",
                    "data": None
                }

            st.session_state.messages.append({
                "role": "assistant",
                "allowed": pipeline_res.get("allowed", False),
                "response_text": pipeline_res.get("response_text", ""),
                "data": pipeline_res.get("data")
            })
            st.rerun()

# --- INTERFACE 2: ADMINISTRATOR DASHBOARD ---
elif interface_mode == "Administrator Dashboard":
    render_audit_logs_view()


