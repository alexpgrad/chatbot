import streamlit as st
import pandas as pd
import json
from math import isnan
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

df = pd.read_csv("postings_with_industry.csv") 

st.set_page_config(page_title="Career Companion Dashboard", page_icon="📊",)

st.title("AI Career Companion Dashboard")
st.sidebar.header("Filters")

st.markdown(
    """
    Welcome to the AI Career Companion Dashboard! Our AI Career Companion dashboard streamlines your job search by offering 
    filtering options such as location, job title, and more. We enhanced this experience using AI-powered summaries of job descriptions. 
    """
)

location = sorted(df["location"].unique().tolist())
selected_location = st.sidebar.selectbox("Select Location", ["All"] + location)  

job_title = sorted(df["title"].unique().tolist())
selected_job_title = st.sidebar.selectbox("Select Job Title", ["All"] + job_title)

industry = sorted(df["industry"].dropna().unique())
selected_industry = st.sidebar.selectbox("Select Company Industry", ["All"] + industry)

work_type = sorted(df["formatted_work_type"].unique().tolist())
selected_work_type = st.sidebar.selectbox("Select Work Type", ["All"] + df["formatted_work_type"].unique().tolist())

experience_level = df["formatted_experience_level"].unique().tolist()
selected_experience_level = st.sidebar.selectbox("Select Experience Level", ["All"] + df["formatted_experience_level"].unique().tolist())

search = st.sidebar.button("Search")

if search: 
    filtered_df = df.copy()

    if selected_job_title != "All":
        filtered_df = filtered_df[filtered_df["title"] == selected_job_title]

    if selected_industry != "All":
        filtered_df = filtered_df[filtered_df["industry"] == selected_industry]

    if selected_location != "All":
        filtered_df = filtered_df[
            filtered_df["location"]
            .str.contains(selected_location, case=False, na=False)
        ]

    if selected_work_type != "All":
        filtered_df = filtered_df[
            filtered_df["formatted_work_type"]
            .str.contains(selected_work_type, case=False, na=False)
        ]

    if selected_experience_level != "All":
        filtered_df = filtered_df[
            filtered_df["formatted_experience_level"]
            .str.contains(selected_experience_level, case=False, na=False)
        ]

    filtered_df = filtered_df.head(10)

    model = OllamaLLM(model = "llama3.2")

    template = """
    You are an expert assistant specialized in matching users to job opportunities based on job listings extracted from our CSV database.
    Your task is to summarize the following job description in one sentence. Do not output any additional text other than the summary. 
    Job description: {description}
    """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    for _, row in filtered_df.iterrows():
        description = row["description"] or ""
        def get_summary(text):
            return chain.invoke({"description": text})
        summary = get_summary(description)
        
        bot_response = json.dumps([{
            "company_name": row["company_name"]
                            if pd.notna(row["company_name"]) else "Not listed",
            "job_title":    row["title"],
            "location":     row["location"],
            "max_salary":   f"{row['max_salary']:.2f} {row['pay_period'].lower()}" 
                                if pd.notna(row["max_salary"]) else "Not listed",
            "experience":   row["formatted_experience_level"]
                            if pd.notna(row["formatted_experience_level"]) else "Not listed",
            "remote_allowed": "Yes" if str(row["remote_allowed"]) == "1" else "Not listed",
            "url":          row["job_posting_url"],
            "industry":     row["industry"],
            "description_summary": summary
        }])

        try:
            matches = json.loads(bot_response)
            for jobs in matches:
                st.markdown(f"""
    **Company: {jobs['company_name']}**  
    *Job Title: {jobs['job_title']}*  
    📍 Location: {jobs['location']}  
    💰 Salary: {jobs['max_salary']}  
    📈 Work-level Experience: {jobs['experience']}  
    📝 Summary: {jobs['description_summary']}  
    🌐 Remote: {jobs['remote_allowed']}  
    🔗 [Apply here]({jobs['url']})
    """)
        except json.JSONDecodeError:
            st.error("Couldn’t parse the AI response.")
            st.write(bot_response)
