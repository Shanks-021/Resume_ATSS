import streamlit as st
import requests

# Backend URL
# API_URL = "http://127.0.0.1:8000/process_resume/"
API_URL = "http://fastapi:8000/process_resume/"


# Streamlit UI
st.title("Smart ATS for Resume Evaluation")

# Input Job Description
jd = st.text_area("Paste the Job Description", height=150)

# Upload Resume
uploaded_file = st.file_uploader("Upload Your Resume", type=["pdf"])

if st.button("Submit"):
    if uploaded_file and jd:
        files = {"file": uploaded_file.getvalue()}
        data = {"job_description": jd}
        
        # Send request to FastAPI backend
        response = requests.post(API_URL, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()  # Ensure it's parsed as JSON

            if "error" in result:
                st.error("Error: " + result["error"])  # Show API error message
            else:
                st.subheader("Evaluation Results")
                st.write(f"**JD Match:** {result.get('JD Match', 'N/A')}")
                st.write(f"**Missing Keywords:** {', '.join(result.get('Missing Keywords', []))}")
                st.write(f"**Profile Summary:** {result.get('Profile Summary', 'No summary provided')}")
        else:
            st.error("Error processing the resume. Try again.")
    else:
        st.warning("Please upload a resume and enter a job description.")
