import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="Medanta Induction Portal",
    layout="wide"
)

# ---- SHOW LOGO SAFELY (NOT IN IFRAME) ----
st.image("mhpl_logo.png", width=180)

# ---- LOAD YOUR EXISTING UI (UNCHANGED) ----
ui_file = Path("ui.html")

if not ui_file.exists():
    st.error("ui.html not found")
else:
    components.html(
        ui_file.read_text(encoding="utf-8"),
        height=1600,
        scrolling=True
    )
