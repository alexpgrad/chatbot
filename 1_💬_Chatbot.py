from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
import streamlit as st
import json
from utils import format_job, format_bot_response

st.set_page_config(page_title="AI Career Companion", page_icon="💼",)
st.title("AI Career Companion")
st.sidebar.header("Career Companion")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

input_text = st.chat_input(
    "Enter your job search queuery: "
)

if input_text:
    with st.spinner("Thinking..."):
        model = OllamaLLM(model="llama3.2")
        template = """
        You are an expert assistant specialized in matching users to job opportunities based on job listings extracted from our CSV database.
        Here are the relevant jobs listings: {jobs}
        Here is the question to answer: {question}
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
        chain = prompt | model
        question = input_text
        jobs = retriever.invoke(question)

        formatted_jobs = [format_job(d) for d in jobs]
        jobs_payload = json.dumps(formatted_jobs, indent=2)
        result = chain.invoke({"jobs": jobs_payload, "question": question})
        st.session_state.chat_history.append({"user": question, "bot": result})

for exchange in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(exchange["user"])
    with st.chat_message("assistant"):
        response = (exchange["bot"])
        format_bot_response(response)

#job_id	company_name ,title, description, max_salary, pay_period, location, min_salary, formatted_work_type, remote_allowed, job_posting_url, skills_desc, industry, formatted_experience_level