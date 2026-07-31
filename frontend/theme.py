import streamlit as st

def apply_production_theme():
    """Applies modern production dark-mode glassmorphism styling."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }

    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #60a5fa 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #9ca3af;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }

    .glass-card {
        background: rgba(17, 24, 39, 0.8);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }

    .trace-step {
        background: rgba(31, 41, 55, 0.6);
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 10px;
        font-size: 0.85rem;
    }

    .badge-allowed {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.78rem;
        letter-spacing: 0.03em;
    }

    .badge-blocked {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.78rem;
        letter-spacing: 0.03em;
    }

    .user-bubble {
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
        color: #ffffff;
        padding: 12px 18px;
        border-radius: 14px 14px 2px 14px;
        margin: 10px 0 10px auto;
        max-width: 80%;
        font-weight: 500;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
    }

    .ai-bubble {
        background: #111827;
        border: 1px solid #1f2937;
        color: #f8fafc;
        padding: 16px 20px;
        border-radius: 14px 14px 14px 2px;
        margin: 10px auto 10px 0;
        max-width: 90%;
        box-shadow: 0 4px 14px rgba(0,0,0,0.2);
    }

    /* Professional Button Styling */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)

