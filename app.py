import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Backend Name: Medanta_Induction
st.set_page_config(page_title="Medanta_Induction Backend")

# 1. Load the Master Quiz Bank
@st.cache_data
def load_bank():
    # Reads the .ods file you've uploaded to GitHub
    return pd.read_excel("Master_Quiz_Bank_FINAL.ods", engine="odf", sheet_name=None)

all_sheets = load_bank()

# 2. Connect to Google Sheets "Bucket"
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Handle the Test Flow
query_params = st.query_params
current_test = query_params.get("test", "BLS") 

if current_test in all_sheets:
    df = all_sheets[current_test]
    st.title(f"Medanta_Induction: {current_test}")
    
    with st.form("assessment_form"):
        user_responses = {}
        for idx, row in df.iterrows():
            st.write(f"**Q{idx+1}: {row['Question']}**")
            # Features 4 options as per your requirement
            options = [row['Option A'], row['Option B'], row['Option C'], row['Option D']]
            user_responses[idx] = st.radio(f"Select Answer for Q{idx+1}", options, key=f"q_{idx}")
        
        submitted = st.form_submit_with_button("Submit to Medanta_Induction Records")
        
        if submitted:
            # Calculate Score
            correct_count = sum(1 for i, r in df.iterrows() if user_responses[i] == r['Correct Answer'])
            final_score = (correct_count / len(df)) * 100
            
            # Data for Google Sheet
            result = {
                "Timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Staff_Name": query_params.get("name", "Unknown"),
                "Staff_ID": query_params.get("id", "N/A"),
                "Score": f"{final_score}%",
                "Status": "Passed" if final_score >= 80 else "Failed"
            }
            
            # Logic: Puts it in the Google Sheet tab named after the test
            conn.update(worksheet=current_test, data=pd.DataFrame([result]))
            st.success(f"Result saved to Medanta_Induction {current_test} sheet!")