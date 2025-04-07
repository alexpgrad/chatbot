from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
import streamlit as st


st.set_page_config(page_title="AI Career Companion", page_icon="💼",)
st.title("AI Career Companion")
st.sidebar.header("Career Companion")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

input_text = st.chat_input(
    "Enter your job search queuery: "
)

if input_text:
    model = OllamaLLM(model="llama3.2")


    template = """
    You are an expert assistant specialized in matching users to job opportunities based on job listings extracted from our CSV database.

    Only use the information provided in the CSV database to answer the user's query.
    Never include any external knowledge or assumptions beyond what is presented here.

    Here are some relevant job listings: {jobs}

    Here is the question to answer: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    question = input_text
    jobs = retriever.invoke(question)
    result = chain.invoke({"jobs": jobs, "question": question})
    print(result)

    st.session_state.chat_history.append({"user": question, "bot": result})

for exchange in st.session_state.chat_history:
    st.markdown(f"**User:** {exchange['user']}")
    st.markdown(f"**Bot:** {exchange['bot']}")
    st.markdown("---")


