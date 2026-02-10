import streamlit as st

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Medanta Assessment",
    layout="centered"
)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("## MEDANTA HOSPITAL LUCKNOW")
st.markdown("---")

# -------------------------------------------------
# READ QUERY PARAM (CORRECT API)
# -------------------------------------------------
params = st.query_params
assessment_id = params.get("assessment")

# -------------------------------------------------
# DEBUG OUTPUT (INTENTIONAL)
# -------------------------------------------------
st.write("DEBUG → assessment param:", assessment_id)

# -------------------------------------------------
# VALIDATION
# -------------------------------------------------
if not assessment_id:
    st.warning("No assessment selected.")
    st.stop()

# -------------------------------------------------
# SUCCESS STATE
# -------------------------------------------------
st.success("App loaded successfully.")
st.info(f"Assessment received: {assessment_id}")

st.markdown(
    """
    ✅ This confirms:
    - Streamlit app starts correctly  
    - Correct file is running (`Induction_portal.py`)  
    - URL parameter is being read  
    - No deprecated APIs  
    """
)
