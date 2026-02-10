import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="Medanta Induction Portal",
    layout="wide"
)

html_path = Path("ui.html")

if not html_path.exists():
    st.error("ui.html file is missing")
else:
    components.html(
        html_path.read_text(encoding="utf-8"),
        height=1600,
        scrolling=True
    )
