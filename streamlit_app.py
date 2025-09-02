import streamlit as st

# Import page modules
from app_pages import pricing, iv_solver, heatmap


st.set_page_config(
    page_title="Option Pricing Calculator",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global typography and layout styling (serious finance tone)
st.markdown(
    """
    <style>
      /* Typography: apply to content elements only, do not override icon fonts */
      html, body {
        font-family: -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif;
      }
      .stMarkdown, p, label, input, textarea, select, button, .stMetric {
        font-family: -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif;
      }
      h1, h2, h3, h4 { letter-spacing: 0.2px; font-weight: 650; }
      .stButton>button { border-radius: 6px; font-weight: 600; }
      .stMetric { border-radius: 6px; }

      /* Keep sidebar permanently visible: hide collapse control */
      [data-testid="stSidebarCollapseControl"] { display: none !important; }

      /* Sidebar title styling */
      [data-testid="stSidebar"] .sidebar-title {
        text-align: center;
        font-weight: 750;
        font-size: 1.35rem;
        line-height: 1.4;
        letter-spacing: 0.3px;
        color: #00b386;
        margin: 0.75rem 0 1.25rem 0; /* extra space below before buttons */
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown('<div class="sidebar-title">Option Analytics</div>', unsafe_allow_html=True)

# Stateful button-based navigation with immediate rerun for correct highlighting
if "page" not in st.session_state:
    st.session_state.page = "Option Pricing"

# Temporarily hide Implied Volatility page; redirect if active
if st.session_state.page == "Implied Volatility":
    st.session_state.page = "Option Pricing"

def _go(page_name: str):
    st.session_state.page = page_name
    try:
        st.rerun()
    except Exception:
        # Backward compatibility with older Streamlit
        try:
            st.experimental_rerun()
        except Exception:
            pass

active = st.session_state.page
st.sidebar.button(
    "Option Pricing",
    key="nav_btn_pricing",
    use_container_width=True,
    type=("primary" if active == "Option Pricing" else "secondary"),
    on_click=_go,
    args=("Option Pricing",),
)
# Implied Volatility navigation hidden for now
st.sidebar.button(
    "Profit Calculator",
    key="nav_btn_heatmap",
    use_container_width=True,
    type=("primary" if active == "Profit Calculator" else "secondary"),
    on_click=_go,
    args=("Profit Calculator",),
)

page = st.session_state.page

if page == "Option Pricing":
    pricing.show_pricing_page()
elif page == "Implied Volatility":
    iv_solver.show_iv_solver_page()
else:
    heatmap.show_heatmap_page()
