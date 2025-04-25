import streamlit as st
from langchain.document_loaders import PyMuPDFLoader
import tempfile
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
import os
import json
from utils import format_job, format_bot_response


def load_pdf(file):
    # Write the uploaded file to a temporary file and return the loaded documents.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_path = tmp_file.name
    try:
        loader = PyMuPDFLoader(tmp_path)
        documents = loader.load()
    finally:
        os.remove(tmp_path)
    return documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

template = """
    You are an expert assistant specialized in matching users to job opportunities based on the 
    following uploaded resume and job listings extracted from our CSV database.

    Candidate resume: {resume_text}

    Here are some relevant job listings: {jobs}

    Strictly follow the instructions below: 
        - DO NOT write any code, prose, or explanations.
        - DO NOT wrap your answer in markdown or backticks.  
        - Return exactly one JSON array (start with `[` and end with `]`).  
        - Each entry must be an object with these keys, in this order:
        1. company_name  
        2. job_title  
        3. location  
        4. max_salary  
        5. experience  
        6. remote_allowed  
        7. url  
        8. industry  
        - Example of desired output:
        ```json
        [
        {{
            "company_name": "...",
            "job_title":    "...",
            "location":     "...",
            "salary":   "...",
            "experience":   "...",
            "remote_allowed": "...",
            "url":          "...",
            "industry":     "..."
        }},
        ]
        ```
        """
prompt = ChatPromptTemplate.from_template(template)
model = OllamaLLM(model="llama3.2")

chain = prompt | model

st.title("Upload Your Resume")

st.markdown(
    """
    Upload your resume in PDF or Word format. Our AI Career Companion will analyze your resume and provide tailored job recommendations.
    """
)

uploaded_file = st.file_uploader("Upload resume: ", type=["pdf"])

if uploaded_file is not None:
    docs = load_pdf(uploaded_file)
    resume_text = format_docs(docs)
    relevant_jobs = retriever.invoke(resume_text)

    formatted_jobs = [format_job(d) for d in relevant_jobs]
    jobs_payload = json.dumps(formatted_jobs, indent=2)

    with st.spinner("Thinking..."):
        chain_input = {
        "resume_text": resume_text,
        "jobs": jobs_payload
        }
        response = chain.invoke(chain_input)

    format_bot_response(response)

    