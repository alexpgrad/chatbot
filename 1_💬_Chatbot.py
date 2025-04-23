from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
import streamlit as st
from math import isnan
import json


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

        def extract_field(page_content: str, prefix: str, default="Not available") -> str:
            for line in page_content.splitlines():
                if line.startswith(prefix):
                    return line[len(prefix):].strip()
            return default
        
        def clean_entry(val, missing="Not listed"):
         if val is None: 
              return missing
         if isinstance(val, float) and isnan(val):
              return missing
         s = str(val).strip()
         if s.lower() == "nan" or s == "":
              return missing
         return s

        def format_job(doc):
            md = doc.metadata
            sal = md.get("max_salary")
            if isinstance(sal, float) and isnan(sal):
                sal = "Not available"
            pay = md.get("pay_period", "")
            title       = extract_field(doc.page_content, "Title: ")
            location    = extract_field(doc.page_content, "Location: ")
            experience  = extract_field(doc.page_content, "Experience Level: ")
            remote_ok   = extract_field(doc.page_content, "Remote Allowed: ")

            return {
                "company_name": md.get("company_name", "Not available"),
                "job_title":    title,
                "location":     location,
                "max_salary":   f"{sal} per {pay}".strip() or "Not available",
                "experience":   clean_entry(experience, "Not specified"),
                "remote_allowed": clean_entry(remote_ok, "Not specified"),
                "url":          clean_entry(md.get("job_posting_url", "Not available")),
                "industry":     clean_entry(md.get("industry", "Not specified")),
            }

        formatted_jobs = [format_job(d) for d in jobs]
        jobs_payload = json.dumps(formatted_jobs, indent=2)
        result = chain.invoke({"jobs": jobs_payload, "question": question})
        st.session_state.chat_history.append({"user": question, "bot": result})

for exchange in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(exchange["user"])
    with st.chat_message("assistant"):
        bot_raw = (exchange["bot"])

        try: 
            matches = json.loads(bot_raw)
            st.markdown("### Matches")
            for jobs in matches: 
                st.markdown(f"""
**Company: {jobs['company_name']}**  
*Job Title: {jobs['job_title']}*  
📍 Location: {jobs['location']}  
💰 Salary: {jobs['max_salary']}  
📈 Work-level Experience: {jobs['experience']}  
🌐 Remote: {jobs['remote_allowed']}  
🔗 [Apply here]({jobs['url']})
""")
        except json.JSONDecodeError:
            st.write(bot_raw)
            st.error("Sorry, I couldn’t decode the response into JSON.")

#job_id	company_name ,title, description, max_salary, pay_period, location, min_salary, formatted_work_type, remote_allowed, job_posting_url, skills_desc, industry, formatted_experience_level