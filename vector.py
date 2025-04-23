from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

df = pd.read_csv("postings_with_industry.csv")
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

db_location = "/Users/chroma_db_c" #working is c
add_documents = not os.path.exists(db_location)

vectore_store = Chroma(
    collection_name="postings",
    embedding_function=embeddings,
    persist_directory=db_location,
)

if add_documents:
    documents = []
    ids = []
    for i, row in df.iterrows():
        page_content = (
            f"Title: {row['title']}\n"
            f"Description: {row['description']}\n"
            f"Location: {row['location']}\n"
            f"Max Salary: {row['max_salary']} per {row['pay_period']}\n"
            f"Experience Level: {row['formatted_experience_level']}\n"
            f"Work Type: {row['formatted_work_type']}\n"
            f"Remote Allowed: {row['remote_allowed']}\n"
            f"Skills: {row['skills_desc']}\n"
            f"Industry: {row['industry']}"
        )
        metadata = {
            "job_id": row["job_id"],
            "company_name": row["company_name"],
            "max_salary": row["max_salary"],
            "min_salary": row["min_salary"],
            "pay_period": row["pay_period"],
            "job_posting_url": row["job_posting_url"],
            "industry": row["industry"]
        }

        document = Document(
            page_content = page_content,
            metadata = metadata,      
            id = str(i)
        )
        ids.append(str(i))
        documents.append(document)

    batch_size = 5000
    for start in range(0, len(documents), batch_size):
        #vectore_store.add_documents(documents = documents[i:i + batch_size], ids=ids[i:i + batch_size])
        batch_docs = documents[start:start+batch_size]
        batch_ids = ids[start:start+batch_size]
        vectore_store.add_documents(documents=batch_docs, ids=batch_ids)

retriever = vectore_store.as_retriever(search_kwargs={"k": 5})
