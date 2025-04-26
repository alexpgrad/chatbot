# AI Career Companion

With over 100,000 job listings in our database, the AI career companion is the ultimate tool to help match prospective job applicants with their dream job. This is made possible through the following features: 

- Chatbot: Our conversational chatbot leverages a large language model powered by OllamaLLM (llama3.2) to give personalized job recommendations and answer career related questions.
- Dashboard: The interactive dashboard offers users a more traditional approach at searching for jobs. Users can filter job listings by salary, location, company industry, and experience level. We use Ollama to summarize the job listing into one concise sentence to significantly reduce the time spent searching for a job that is a good fit. 
- Resume Analyzer: This feature lets users upload their resume (in PDF format), which then undergoes text extraction. Next, the user's key skills and experiences are embedded using an Ollama generated vector representation. We then store these embeddings in ChromaDB to  match users with relevant job listings that match their skills and background. 
- Databse: To train our LLM, we downloaded a dataset from Kaggle.com. This dataset has 124,000 LinkedIn job postings from various industries. This dataset has several insightful attributes, such as title, salary, location, etc. The dataset can be found at this [URL](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings)
- UI: Streamlit is used to offer a user-friendly and interactive web interface.  

## Getting started 

1. Clone repository: 
```
git clone https://github.com/alexpgrad/chatbot
cd JOB_AGENT_CHATBOT
```

2. Download dataset:

    The dataset can be downloaded from the link provided above. 

3. Setup a virtual environment: 

```
python3 -m venv venv
source venv/bin/activate

``` 

4. Run the app: 

```
sudo streamlit 1_💬_Chatbot.py 

```