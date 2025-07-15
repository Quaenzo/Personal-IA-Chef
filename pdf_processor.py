import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import streamlit as st 

load_dotenv()

PDF_PATH = "The_Flavour_Thesaurus.pdf"
VECTOR_DB_PATH = "faiss_abbinamenti_db"

def process_pdf_and_create_vector_db():
    """Load the PDF file, split it to chuncks, create embeddings and save in FAISS"""
    
    if os.path.exists(VECTOR_DB_PATH):
        print(f"Vector Database '{VECTOR_DB_PATH}' already exists. Skipping the creation of it.")
        return 
    
    print(f"Loading PDF from: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"Loaded {len(documents)} pages from the PDF file.")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 200
    )
    
    texts = text_splitter.split_documents(documents)
    print(f"The PDF file is been splitted into {len(texts)} chunks.")
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print("Starting HuggingFace's embeddings...")
    
    print("Creating FAISS vector database...")
    db = FAISS.from_documents(texts, embeddings)
    db.save_local(VECTOR_DB_PATH)
    print(f"FAISS vector database saved correctly in : {VECTOR_DB_PATH}")
    

def get_abbinamenti_retriever():
    """Load up the FAISS vector database and return a retriever"""
    hugging_key = st.secrets['HUGGINGFACE_API_KEY']
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", api_key=)
    db = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
    return db.as_retriever(search_kwargs={"k" : 5})

if __name__ == "__main__":
    process_pdf_and_create_vector_db()