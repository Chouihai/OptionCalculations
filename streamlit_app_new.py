import streamlit as st
import sys
import os

# Add the mvp package to the path so we can import it
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import page modules
from pages import home, pricing, iv_solver, heatmap

# Page configuration
st.set_page_config(
    page_title="Option Pricing Calculator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stMetric {
        background-color: white;
        padding: 0.5rem;
        border-radius: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📊 Option Calculator")
st.sidebar.markdown("---")

# Main content
if st.sidebar.button("🏠 Home", use_container_width=True):
    st.session_state.page = "home"

if st.sidebar.button("💰 Option Pricing", use_container_width=True):
    st.session_state.page = "pricing"

if st.sidebar.button("🔍 IV Solver", use_container_width=True):
    st.session_state.page = "iv"

if st.sidebar.button("📊 PnL Heatmap", use_container_width=True):
    st.session_state.page = "heatmap"

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"

# Page routing
if st.session_state.page == "home":
    home.show_home_page()
elif st.session_state.page == "pricing":
    pricing.show_pricing_page()
elif st.session_state.page == "iv":
    iv_solver.show_iv_solver_page()
elif st.session_state.page == "heatmap":
    heatmap.show_heatmap_page()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    Built with Streamlit • Black-Scholes-Merton Model • Educational Tool
</div>
""", unsafe_allow_html=True)
