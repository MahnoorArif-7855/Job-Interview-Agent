import streamlit as st
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in .env file")
# Title
st.title("📄 AI Job Interview Assistant")

# Upload Resume PDF
resume_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
jd_text = st.text_area("Paste Job Description")

if st.button("Analyze") and resume_file and jd_text:
    with st.spinner("Processing..."):
        # Load Resume
        resume_path = "resume.pdf"
        with open(resume_path, "wb") as f:
            f.write(resume_file.getbuffer())
        resume_docs = PyPDFLoader(resume_path).load()

        # Convert JD text into LangChain docs
        jd_docs = [Document(page_content=jd_text, metadata={"source": "job_description"})]

        # Create embeddings
        embeddings = OpenAIEmbeddings()

        # Create vector stores
        resume_db = Chroma.from_documents(resume_docs, embeddings, collection_name="resume_data")
        jd_db = Chroma.from_documents(jd_docs, embeddings, collection_name="job_description_data")

        # Init LLM
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        # Skill Gap Analysis
        qa_template = """
        Compare the following Resume with the Job Description.
        Highlight:
        1. Matching Skills
        2. Missing Skills
        3. Recommendations for improvement

        Resume: {resume}
        Job Description: {jd}
        """
        prompt = PromptTemplate(template=qa_template, input_variables=["resume", "jd"])
        qa_chain = prompt.format(resume=resume_docs[0].page_content, jd=jd_text)

        response = llm.predict(qa_chain)

        # Output
        st.subheader("📊 Analysis")
        st.write(response)

        # Interview Questions
        q_template = """
        Based on this job description:
        {jd}
        Generate 5 technical and 5 behavioral interview questions.
        """
        q_prompt = PromptTemplate(template=q_template, input_variables=["jd"])
        questions = llm.predict(q_prompt.format(jd=jd_text))

        st.subheader("🎤 Interview Questions")
        st.write(questions)
