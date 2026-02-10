import streamlit as st
import pandas as pd
import time
import requests

# 1. THE BRIDGE LINK (The "Writer" - sends scores to Google Sheets)
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbxVOThjR83HnI6LzxX2uMsAdGaI5nKnBIuwfVq83zLYYUcF-aOpTGPLdY2F5kLbeWn8/exec"

# 2. ASSESSMENT LINKS (The "Readers" - pulls questions from Google Sheets)
ASSESSMENT_LINKS = {
    "HR_ADMIN_PROCESS": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=0&single=true&output=csv",
    "SECOND_VICTIM": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=2088706673&single=true&output=csv",
    "Medication_Safety": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=892298814&single=true&output=csv",
    "Blood_Blood_Product": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=160379599&single=true&output=csv",
    "Basic_Life_Support": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=2095344397&single=true&output=csv",
    "Fire_Safety": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=1869165187&single=true&output=csv",
    "Infection_Prevention": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=1217118319&single=true&output=csv",
    "Quality_Training": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=628654756&single=true&output=csv",
    "IPSG": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=243004079&single=true&output=csv",
    "Facility_Mgmt_Safety": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=970108257&single=true&output=csv",
    "Emergency_Codes": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=821088497&single=true&output=csv",
    "Cybersecurity_Assessment": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=1771711881&single=true&output=csv",
    "Workplace_Violence": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=1754665265&single=true&output=csv",
    "EMR_Training": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=629824401&single=true&output=csv",
    "HIS_Training": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=1228613998&single=true&output=csv",
    "Medical_Documentation": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRtPu9Ul7H7cScYBHluogzLNkDzsST-bBgKlN_wUI1qwpMOzazyGH6moUNZBIoL9LPjgZUIQBJ-6x0Y/pub?gid=1507714537&single=true&output=csv"
}

st.set_page_config(page_title="Medanta Assessment Portal", layout="wide")

# Get parameters passed from the HTML
params = st.query_params
test_key = params.get("test", "Basic_Life_Support")
staff_id = params.get("id", "N/A")
staff_name = params.get("name", "Staff")

# 2. Timer Logic (10 Minutes)
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()

elapsed = time.time() - st.session_state.start_time
remaining = max(0, 600 - int(elapsed))

if remaining <= 0:
    st.error("⏰ Time Expired! Please close this window and restart the assessment.")
    st.stop()

# Sidebar Timer Display
mins, secs = divmod(remaining, 60)
st.sidebar.markdown(f"## ⏳ {mins:02d}:{secs:02d}")
st.sidebar.write(f"**Staff:** {staff_name} | **ID:** {staff_id}")

# 3. Quiz Logic: Loading Questions & Options
if test_key in ASSESSMENT_LINKS:
    try:
        df = pd.read_csv(ASSESSMENT_LINKS[test_key])
        
        # Prevent 'Division by Zero' error if sheet is empty
        if df.empty:
            st.error("Sheet is empty. Please verify the Google Sheet data.")
        else:
            with st.form("quiz_form"):
                st.title(f"📝 {test_key.replace('_', ' ')}")
                responses = {}
                
                for i, row in df.iterrows():
                    st.write(f"**Q{i+1}: {row['Question']}**")
                    # Dynamically collect options A through D
                    options = [str(row[opt]) for opt in ['Option A', 'Option B', 'Option C', 'Option D'] if pd.notna(row[opt])]
                    responses[i] = st.radio(f"Choose answer", options, key=f"q{i}", index=None)
                
                if st.form_submit_button("Submit Final Answers"):
                    # Scoring logic
                    correct = sum(1 for idx, r in df.iterrows() if responses[idx] == str(r['Correct Answer']))
                    score = round((correct / len(df)) * 100, 2)
                    
                    if score >= 80:
                        st.success(f"🎉 PASSED! Score: {score}%")
                        # Package data for Master Result Sheet
                        payload = {
                            "Staff_Name": staff_name, "Staff_ID": staff_id,
                            "Assessment": test_key, "Score": f"{score}%", "Status": "Pass"
                        }
                        requests.post(BRIDGE_URL, json=payload)
                        st.balloons()
                    else:
                        st.error(f"❌ Score: {score}%. 80% required to pass. Please reattempt.")
    except Exception as e:
        st.error(f"Error loading questions: {e}")
        st.error(f"Error loading assessment: {e}")
else:
    st.warning("Assessment module not found. Please contact the administrator.")

