import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# -------------------------------
# BASIC APP CONFIG
# -------------------------------
st.set_page_config(
    page_title="Medanta Induction Portal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------
# HIDE STREAMLIT DEFAULT UI
# -------------------------------
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { background-color: #f4f6f8; }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# LOAD HTML UI ONLY
# -------------------------------
html_path = Path("ui.html")

if not html_path.exists():
    st.error("❌ ui.html not found. Please upload ui.html to the repository root.")
    st.stop()

# -------------------------------
# RENDER YOUR EXISTING UI
# -------------------------------
components.html(
    html_path.read_text(encoding="utf-8"),
    height=1400,
    scrolling=True
)

# -------------------------------
# STOP STREAMLIT FROM RENDERING ANYTHING ELSE
# -------------------------------
st.stop()
