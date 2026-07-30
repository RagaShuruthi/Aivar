import streamlit as st
import requests
from app.agent.customer_agent import AICustomerAgent
from app.db.session import SessionLocal

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

def render_assistant_page():
    st.markdown('<div class="gradient-title">🤖 AI Customer Assistant</div>', unsafe_allow_html=True)
    st.markdown("##### *Powered by Gemini 2.5 Flash & Protected by Tool Permission Enforcer*")
    st.divider()

    # Agent Role & Session Context Control Bar
    col_agent, col_session, col_clear = st.columns([2, 2, 1])
    
    with col_agent:
        selected_agent = st.selectbox(
            "Active Agent Manifest Role",
            ["support_agent", "admin_agent", "restricted_agent"],
            help="support_agent: Read-only (session customer)\nadmin_agent: Full CRUD (global)\nrestricted_agent: Blocked"
        )

    with col_session:
        session_customer_id = st.number_input(
            "Active Session Context Customer ID",
            min_value=100,
            max_value=999,
            value=101,
            help="Simulates current logged-in customer identity context"
        )

    with col_clear:
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_trace = None
            st.rerun()

    st.markdown("<br/>", unsafe_allow_html=True)

    # Initialize Chat History & Last Trace in Session State
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am your Enterprise AI Assistant. I can help you query or manage customer profile details in the CRM.\n\n"
                    "🔒 *All my tool calls pass through the Tool Permission Proxy before touching any customer records.*"
                )
            }
        ]

    if "last_trace" not in st.session_state:
        st.session_state.last_trace = None

    # Main Grid: Left side Chat Interface (7 columns), Right side Live Governance Inspector (5 columns)
    chat_col, inspector_col = st.columns([7, 5])

    with chat_col:
        st.subheader("💬 Natural Language Conversation")

        # Quick Sample Prompt Chips
        st.markdown("**Quick Prompts:**")
        chip_col1, chip_col2, chip_col3 = st.columns(3)
        prompt_to_send = None
        if chip_col1.button("📋 Show Customer 101", use_container_width=True):
            prompt_to_send = "Show profile details for customer 101"
        if chip_col2.button("✏️ Update Customer 101", use_container_width=True):
            prompt_to_send = "Update customer 101 name to Alice Vance"
        if chip_col3.button("❌ Delete Customer 101", use_container_width=True):
            prompt_to_send = "Delete customer 101 from CRM"

        # Render Chat History
        chat_container = st.container(height=420)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Chat Input
        user_input = st.chat_input("Ask assistant e.g. 'Show details for customer 101' or 'Delete customer 101'...")
        if user_input:
            prompt_to_send = user_input

        # Process Message
        if prompt_to_send:
            # Append user message
            st.session_state.messages.append({"role": "user", "content": prompt_to_send})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt_to_send)

            # Process through AICustomerAgent
            with st.spinner("🤖 Gemini extracting intent & validating with Permission Engine..."):
                db = SessionLocal()
                try:
                    agent_result = AICustomerAgent.process_query(
                        db=db,
                        prompt=prompt_to_send,
                        agent_id=selected_agent,
                        session_customer_id=session_customer_id
                    )
                    st.session_state.last_trace = agent_result
                    bot_text = agent_result["response"]

                    # Append assistant message
                    st.session_state.messages.append({"role": "assistant", "content": bot_text})
                    with chat_container:
                        with st.chat_message("assistant"):
                            st.markdown(bot_text)

                except Exception as e:
                    err_msg = f"Error processing query: {e}"
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
                    st.error(err_msg)
                finally:
                    db.close()

            st.rerun()

    # Right Column: Real-Time Governance Inspector Panel
    with inspector_col:
        st.subheader("🛡️ Live Governance Inspector")
        st.caption("Real-Time Policy Decision Point (PDP) Inspection")

        trace = st.session_state.last_trace

        if trace:
            decision = trace.get("permission_decision", {})
            allowed = trace.get("allowed", False)

            # Status Badge Header
            if allowed:
                st.markdown('<div class="badge-allowed">🟢 STATUS: 200 ALLOWED (FORWARDED TO CRM)</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="badge-blocked">🔴 STATUS: 403 FORBIDDEN (BLOCKED BY PROXY)</div>', unsafe_allow_html=True)

            st.markdown("<br/>", unsafe_allow_html=True)

            # Tabbed Inspector Details
            t1, t2, t3 = st.tabs(["📋 Tool Call Payload", "📜 Manifest Rules", "📝 Audit Record"])

            with t1:
                st.markdown("**Extracted Payload (Sent to Proxy):**")
                st.json(trace.get("tool_call_payload", {}))

            with t2:
                st.markdown("**Evaluated Decision Reasoning:**")
                st.info(decision.get("reason", "No evaluation details"))
                st.markdown(f"- **Agent Role:** `{selected_agent}`")
                st.markdown(f"- **Target Operation:** `{decision.get('operation', 'N/A')}`")
                st.markdown(f"- **Target Customer ID:** `{decision.get('target_customer_id', 'N/A')}`")
                st.markdown(f"- **Active Session Context:** `{session_customer_id}`")

            with t3:
                st.markdown(f"**SQLite Audit Log Record ID:** `{trace.get('audit_log_id', 'N/A')}`")
                if trace.get("data"):
                    st.markdown("**Returned CRM Payload:**")
                    st.json(trace["data"])
                else:
                    st.warning("No data returned (Request Blocked or Record Not Found).")
        else:
            st.markdown("""
            <div class="glass-card" style="text-align: center; color: #9ca3af; padding: 40px 20px;">
                🔍 Send a message in the chat to observe real-time policy manifest evaluations, payload extractions, and 403 denial reports!
            </div>
            """, unsafe_allow_html=True)
