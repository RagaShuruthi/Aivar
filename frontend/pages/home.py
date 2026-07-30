import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

def render_home_page():
    st.markdown('<div class="gradient-title">Enterprise AI Governance Platform</div>', unsafe_allow_html=True)
    st.markdown("##### *Zero-Trust Security & Fine-Grained Tool Permission Enforcer for Autonomous AI Agents*")
    st.divider()

    # System Liveness & Health Banner
    col_status, col_seed = st.columns([3, 1])
    with col_status:
        try:
            res = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if res.status_code == 200:
                st.markdown(
                    '<span class="badge-allowed">🟢 BACKEND SYSTEM HEALTHY & ONLINE</span> '
                    '<span style="color:#9ca3af; font-size:0.85rem; margin-left:10px;">FastAPI Gateway: Port 8000 | SQLite Persistent Engine Active</span>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown('<span class="badge-blocked">🔴 BACKEND HEALTH UNHEALTHY</span>', unsafe_allow_html=True)
        except Exception:
            st.markdown('<span class="badge-blocked">🔴 API GATEWAY UNREACHABLE (Start server using python run_all.py)</span>', unsafe_allow_html=True)

    with col_seed:
        if st.button("🌱 Seed CRM Mock DB", type="secondary", use_container_width=True):
            try:
                r = requests.post(f"{API_BASE_URL}/api/v1/crm/seed")
                if r.status_code == 201:
                    st.toast("✅ Database seeded with Customers 101, 102, 103!", icon="🌱")
                else:
                    st.toast("Database already contains customer data.", icon="ℹ️")
            except Exception as e:
                st.error(f"Error seeding DB: {e}")

    st.markdown("<br/>", unsafe_allow_html=True)

    # Architecture Overview Section
    st.subheader("🏛️ Zero-Trust Security Architecture")
    st.markdown("""
    In enterprise AI deployments, giving autonomous LLM agents direct database or API access presents severe prompt injection and data breach risks.
    This platform sits between the **AI Assistant (Gemini)** and **Enterprise APIs (CRM)** to enforce fine-grained **Attribute-Based Access Control (ABAC)** policies on every tool call.
    """)

    st.markdown("""
    ```
    ┌─────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
    │  Human User │ ────► │ AI Customer Assistant│ ────► │  Gemini 2.5 Flash    │
    └─────────────┘       │  (Role & Context)    │       │  (Intent Extractor)  │
                          └──────────────────────┘       └──────────┬───────────┘
                                                                    │
                                                                    ▼
    ┌─────────────────────────┐       ┌─────────────────────────────────────────┐
    │ Enterprise Mock CRM API │ ◄──── │ Tool Permission Proxy Gateway (FastAPI) │
    │   (SQLite Persistence)  │ ALLOW │ ┌─────────────────────────────────────┐ │
    └────────────┬────────────┘       │ │      Permission Engine (PDP)        │ │
                 │                    │ │  Evaluates JSON Manifest & Session  │ │
                 │                    │ └─────────────────────────────────────┘ │
                 ▼                    └────────────────────┬────────────────────┘
    ┌─────────────────────────┐                            │ BLOCKED (403)
    │  SQLite Audit Logging   │ ◄──────────────────────────┘
    │  & Automated Alerting   │
    └─────────────────────────┘
    ```
    """)

    st.divider()

    # Core Security Features Cards
    st.subheader("🛡️ Core AI Governance Capabilities")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("""
        <div class="glass-card">
            <h4>🔐 Zero Trust & Least Privilege</h4>
            <p style="color:#9ca3af; font-size:0.85rem;">
                No LLM has raw database credentials. Every tool call is intercepted and validated against declarative JSON manifests.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="glass-card">
            <h4>⚡ Microsecond PDP Engine</h4>
            <p style="color:#9ca3af; font-size:0.85rem;">
                Evaluates operation whitelists, tool authorizations, and session context matches deterministically in sub-milliseconds.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="glass-card">
            <h4>📜 Non-Repudiable Audit</h4>
            <p style="color:#9ca3af; font-size:0.85rem;">
                Persists immutable, timestamped logs for every allowed and blocked request to fulfill NIST AI RMF standards.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="glass-card">
            <h4>🚨 Automated Threat Alerts</h4>
            <p style="color:#9ca3af; font-size:0.85rem;">
                Detects policy violation spikes (>3 blocked requests per session) and triggers high-priority SOC alerts.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # API Quick Reference
    st.subheader("🔌 Gateway Endpoint Reference")
    api_df = [
        {"Endpoint": "/api/v1/agent/chat", "Method": "POST", "Description": "Conversational AI Assistant query endpoint mediated by Gemini & Permission Engine"},
        {"Endpoint": "/api/v1/proxy/invoke-tool", "Method": "POST", "Description": "Direct Tool Call Proxy gateway enforcing ABAC manifest validation"},
        {"Endpoint": "/api/v1/audit/logs", "Method": "GET", "Description": "Paginated audit logs retrieval with status and agent filters"},
        {"Endpoint": "/api/v1/audit/stats", "Method": "GET", "Description": "Real-time governance analytics and block rate KPIs"},
        {"Endpoint": "/api/v1/audit/alerts", "Method": "GET", "Description": "Active threat breach alerts generated when violations exceed threshold"}
    ]
    st.table(api_df)
