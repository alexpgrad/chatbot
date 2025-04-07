import streamlit as st
from langchain.document_loaders import PyMuPDFLoader
import tempfile
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
import os

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

    Based on the candidate's resume and the job listings, please provide tailored job recommendations including job title, company, and key details.

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
    jobs_text = format_docs(relevant_jobs)

    chain_input = {
        "resume_text": resume_text,
        "jobs": jobs_text
    }
    result = chain.invoke(chain_input)

    st.subheader("Tailored Job Recommendations")
    st.write(result)

