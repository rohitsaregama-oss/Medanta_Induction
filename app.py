import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuration & Mapping of All Shared Links
ASSESSMENT_LINKS = {
    "HR_ADMIN_PROCESS": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=0&single=true&output=csv",
    "SECOND_VICTIM": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)",
    "Medication_Safety": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)",
    "Blood_Blood_Product": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)",
    "Basic_Life_Support": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)",
    "Fire_Safety": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)",
    "Infection_Prevention": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)",
    "Quality_Training": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)",
    "IPSG": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)",
    "Facility_Mgmt_Safety": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)",
    "Emergency_Codes": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)",
    "Cybersecurity_Assessment": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)",
    "Workplace_Violence": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)",
    "EMR_Training": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)",
    "HIS_Training": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)",
    "Medical_Documentation": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUI (rest of link...)"
}

st.set_page_config(page_title="Medanta_Induction Assessment")
conn = st.connection("gsheets", type=GSheetsConnection)

# Get parameters from HTML
params = st.query_params
test_type = params.get("test", "Basic_Life_Support")
staff_id = params.get("id", "N/A")
staff_name = params.get("name", "Staff")

# 2. Timer Logic (10 Minutes / 600 Seconds)
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()

elapsed = time.time() - st.session_state.start_time
remaining = max(0, 600 - int(elapsed))

if remaining <= 0:
    st.error("Time Up! You must reattempt the assessment.")
    if st.button("Restart"):
        del st.session_state.start_time
        st.rerun()
else:
    mins, secs = divmod(remaining, 60)
    st.sidebar.header(f"Time: {mins:02d}:{secs:02d}")

# 3. Assessment Quiz
if test_type in ASSESSMENT_LINKS:
    df = pd.read_csv(ASSESSMENT_LINKS[test_type])
    
    with st.form("quiz_form"):
        st.title(f"{test_type.replace('_', ' ')}")
        responses = {}
        for i, row in df.iterrows():
            st.write(f"**Q{i+1}: {row['Question']}**")
            options = [row['Option A'], row['Option B'], row['Option C'], row['Option D']]
            responses[i] = st.radio(f"Choose answer", options, key=f"q{i}")
        
        if st.form_submit_button("Submit Assessment"):
            correct = sum(1 for idx, r in df.iterrows() if responses[idx] == r['Correct Answer'])
            score = (correct / len(df)) * 100
            
            # 4. Pass/Fail Logic (80% Threshold)
            if score >= 80:
                st.success(f"Passed! Score: {score}%")
                res = {"Timestamp": pd.Timestamp.now(), "Staff_ID": staff_id, "Score": f"{score}%", "Status": "Pass"}
                conn.update(worksheet=test_type, data=pd.DataFrame([res]))
                st.balloons()
            else:
                st.error(f"Failed (Score: {score}%). 80% required to pass. Please reattempt.")
                if st.button("Try Again"):
                    del st.session_state.start_time
                    st.rerun()

