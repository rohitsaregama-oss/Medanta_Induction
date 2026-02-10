import streamlit as st

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Medanta Assessment",
    layout="centered"
)

# -------------------------------------------------
# SAFE HEADER (NO EXTERNAL DEPENDENCIES)
# -------------------------------------------------
st.markdown("## MEDANTA HOSPITAL LUCKNOW")
st.markdown("---")

# -------------------------------------------------
# READ QUERY PARAM (CORRECT, NON-DEPRECATED)
# -------------------------------------------------
params = st.query_params
assessment_id = params.get("assessment")

# -------------------------------------------------
# DEBUG OUTPUT (TEMPORARY BUT INTENTIONAL)
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
    This confirms:
    - The app starts without error  
    - The URL is correct  
    - Query parameters are working  
    """
)
