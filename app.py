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

# 2. Setup the App
st.set_page_config(page_title="Medanta_Induction Assessment")
conn = st.connection("gsheets", type=GSheetsConnection)

# Get URL parameters from your HTML frontend
params = st.query_params
test_type = params.get("test", "Basic_Life_Support")
staff_name = params.get("name", "New Staff")
staff_id = params.get("id", "0000")

st.title(f"Medanta {test_type.replace('_', ' ')} Assessment")

# 3. Dynamic Question Logic
if test_type in ASSESSMENT_LINKS:
    try:
        df = pd.read_csv(ASSESSMENT_LINKS[test_type])
        
        with st.form("assessment_form"):
            responses = {}
            for i, row in df.iterrows():
                st.write(f"**Q{i+1}: {row['Question']}**")
                options = [row['Option A'], row['Option B'], row['Option C'], row['Option D']]
                responses[i] = st.radio(f"Select answer for Q{i+1}", options, key=f"q{i}")
            
            if st.form_submit_button("Submit Assessment"):
                # Score calculation
                correct = sum(1 for idx, r in df.iterrows() if responses[idx] == r['Correct Answer'])
                score_pct = (correct / len(df)) * 100
                
                # Flow data to Google Sheet result tab
                result = {
                    "Timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                    "Staff_Name": staff_name,
                    "Staff_ID": staff_id,
                    "Score": f"{score_pct}%",
                    "Status": "Passed" if score_pct >= 80 else "Failed"
                }
                conn.update(worksheet=test_type, data=pd.DataFrame([result]))
                
                st.success(f"Submitted! Score: {score_pct}%")
                st.balloons()
    except Exception as e:
        st.error("Error loading assessment. Please check your network connection.")
