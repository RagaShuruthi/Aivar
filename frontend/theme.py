import streamlit as st

def apply_production_theme():
    """Applies modern production dark-mode glassmorphism styling."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }

    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
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
        padding: 16px;
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
        border: 1px solid #10b981;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.8rem;
    }

    .badge-blocked {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid #ef4444;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.8rem;
    }

    .user-bubble {
        background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%);
        color: #ffffff;
        padding: 12px 16px;
        border-radius: 16px 16px 4px 16px;
        margin: 10px 0 10px auto;
        max-width: 80%;
    }

    .ai-bubble {
        background: #1e293b;
        border: 1px solid #334155;
        color: #f8fafc;
        padding: 14px 18px;
        border-radius: 16px 16px 16px 4px;
        margin: 10px auto 10px 0;
        max-width: 90%;
    }
    </style>
    """, unsafe_allow_html=True)
