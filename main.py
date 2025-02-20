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