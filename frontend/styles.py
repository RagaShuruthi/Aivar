import streamlit as st

def apply_enterprise_styles():
    """Applies custom Enterprise SaaS CSS design system inspired by Stripe, Azure, and Vercel."""
    st.markdown("""
        <style>
        /* Import Modern Typography from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Background Theme */
        .stApp {
            background-color: #0b0f19;
            color: #f3f4f6;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #111827;
            border-right: 1px solid #1f2937;
        }

        /* Glassmorphism Containers */
        .glass-card {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: all 0.3s ease-in-out;
        }
        .glass-card:hover {
            border-color: rgba(99, 102, 241, 0.4);
            transform: translateY(-2px);
        }

        /* Metric Glowing Widgets */
        .metric-container {
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .metric-label {
            font-size: 0.85rem;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 4px;
        }

        /* Threat Alert Banner */
        .threat-alert-box {
            background: linear-gradient(90deg, rgba(239, 68, 68, 0.2) 0%, rgba(185, 28, 28, 0.4) 100%);
            border: 1px solid #ef4444;
            border-radius: 10px;
            padding: 18px 24px;
            color: #fef2f2;
            margin-bottom: 24px;
            box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
        }

        /* Badges */
        .badge-allowed {
            background-color: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 600;
            display: inline-block;
        }
        .badge-blocked {
            background-color: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 600;
            display: inline-block;
        }

        /* Header Gradient */
        .gradient-title {
            font-size: 2.4rem;
            font-weight: 800;
            background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }

        /* Tab Custom Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: #111827;
            padding: 8px;
            border-radius: 10px;
            border: 1px solid #1f2937;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            color: #9ca3af;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1f2937 !important;
            color: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)
