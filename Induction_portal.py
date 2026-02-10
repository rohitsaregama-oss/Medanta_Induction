import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="Medanta Induction Portal",
    layout="wide"
)

ui_path = Path("ui.html")

if not ui_path.exists():
    st.error("ui.html not found. Please upload ui.html to the repository root.")
else:
    components.html(
        ui_path.read_text(encoding="utf-8"),
        height=1400,
        scrolling=True
    )
