from fastapi import FastAPI, File, UploadFile, Form
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json  # Import JSON module

# Load API key
load_dotenv()
print(os.getenv("GOOGLE_API_KEY")) 
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize FastAPI
app = FastAPI()

# Function to extract text from PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        text += str(reader.pages[page].extract_text())
    return text

# Function to get response from Gemini
def get_gemini_response(text, jd):
    input_prompt = f"""
    Hey, act like a skilled ATS (Application Tracking System) with expertise in software engineering, data science, 
    data analytics, and big data. Evaluate the resume based on the job description.

    Resume: {text}
    Job Description: {jd}

    Your response *must strictly follow* this JSON format:
    {{
      "JD Match": "XX%",  
      "Missing Keywords": ["keyword1", "keyword2", "keyword3"],  
      "Profile Summary": "Brief profile summary here."
    }}

    ONLY return a valid JSON response, nothing else.
    """

    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_prompt)

    # Ensure response is parsed as JSON
    try:
        return json.loads(response.text)  # Convert response to Python dictionary
    except json.JSONDecodeError:
        return {"error": "Invalid response format from Gemini"}

# FastAPI Route to Process Resume
@app.post("/process_resume/")
async def process_resume(job_description: str = Form(...), file: UploadFile = File(...)):
    text = input_pdf_text(file.file)  # Extract text from PDF
    response = get_gemini_response(text, job_description)  # Send data to Gemini
    return response  # Returning structured JSON



import streamlit as st
import requests

# Backend URL
API_URL = "http://127.0.0.1:8000/process_resume/"

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
