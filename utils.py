from math import isnan
import streamlit as st
import json 

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
        sal = "Not listed"
    if sal is None:
        sal = "Not listed"
    if isinstance(sal, str) and not sal.strip():
        sal = "Not listed"

    pay = md.get("pay_period", "").lower()
    title       = extract_field(doc.page_content, "Title: ")
    location    = extract_field(doc.page_content, "Location: ")
    experience  = extract_field(doc.page_content, "Experience Level: ")
    remote_ok   = extract_field(doc.page_content, "Remote Allowed: ")
    return {
        "company_name": md.get("company_name", "Not available"),
        "job_title":    title,
        "location":     location,
        "max_salary":   f"{sal} {pay}".strip() or "Not listed",
        "experience":   clean_entry(experience, "Not listed"),
        "remote_allowed": clean_entry(remote_ok, "Not listed"),
        "url":          clean_entry(md.get("job_posting_url", "Not listed")),
        "industry":     clean_entry(md.get("industry", "Not listed")),
            }

#"remote_allowed": "Yes" if str(row["remote_allowed"]) == "1" else "Not listed",

def format_bot_response(response):
    try: 
        matches = json.loads(response)
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
        st.write(response)
        st.error("Sorry, I couldn’t decode the response into JSON.")