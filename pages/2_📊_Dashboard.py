import streamlit as st
import pandas as pd

df = pd.read_csv("postings_with_industry.csv") 

st.set_page_config(page_title="Career Companion Dashboard", page_icon="📊",)

st.title("AI Career Companion Dashboard")
st.sidebar.header("Filters")

st.markdown(
    """
    Welcome to the AI Career Companion Dashboard! Our AI Career Companion dashboard streamlines your job search by offering 
    filtering options such as salary and location. We enhanced this experience using AI-powered summaries of job descriptions. 
    """
)

#st.subheader("Filter Job Postings")
#st.markdown(
 #   """
  #  Use the filters below to narrow down your job search. You can filter by salary range, location, and other criteria.
   # """
#)

min_salary = int(df["min_salary"].min())
max_salary = int(df["max_salary"].max())

salary_range = st.sidebar.slider("Select Salary Range", min_salary, max_salary, (min_salary, max_salary))

location = df["location"].unique().tolist()
selected_location = st.sidebar.selectbox("Select Location", ["All"] + location)  

industry = df["industry"].unique().tolist() 
selected_industry = st.sidebar.selectbox("Select Industry", ["All"] + industry)

work_type = df["formatted_work_type"].unique().tolist()
selected_work_type = st.sidebar.selectbox("Select Work Type", ["All"] + work_type)

experience_level = df["formatted_experience_level"].unique().tolist()
selected_experience_level = st.sidebar.selectbox("Select Experience Level", ["All"] + experience_level)


filtered_df = df[
    (df["min_salary"] >= salary_range[0]) & 
    (df["max_salary"] <= salary_range[1])
]
if selected_location != "All":
    filtered_df = filtered_df[filtered_df["location"] == selected_location]
if selected_industry != "All":
    filtered_df = filtered_df[filtered_df["industry"] == selected_industry]

st.write(filtered_df)
