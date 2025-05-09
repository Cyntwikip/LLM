import streamlit as st
import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
import openai
from openai import AzureOpenAI

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI API configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

# Initialize Azure OpenAI client
azure_openai_client = AzureOpenAI(
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)

# Initialize ChromaDB client
CHROMA_DATA_PATH = "./chromadb"  # Path to the ChromaDB data directory
chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

def embed_query_azure(query):
    """
    Generate an embedding for a query using Azure OpenAI's API.
    """
    try:
        response = azure_openai_client.embeddings.create(
            input=query,  # Pass the entire list of texts
            model=AZURE_OPENAI_DEPLOYMENT_NAME  # Use the deployment name as the engine
        )
        return response.data[0].embedding
    except Exception as e:
        raise Exception(f"Azure OpenAI API error: {e}")

def query_chromadb(query, top_k=5):
    """
    Query ChromaDB for the most relevant chunks based on the query.
    """
    # Generate embedding for the query
    query_embedding = embed_query_azure(query)

    # Retrieve the most relevant chunks from ChromaDB
    collection_name = "genie_text_metadata"
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_functions.OpenAIEmbeddingFunction(
            api_key=AZURE_OPENAI_API_KEY,
            model_name=AZURE_OPENAI_DEPLOYMENT_NAME
        )
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results

def summarize_results(query, documents):
    """
    Summarize the retrieved documents in the context of the query using Azure OpenAI's GPT model.
    """
    try:
        # Prepare the prompt for summarization
        prompt = f"""
        You are an assistant that summarizes information in the context of a user's query.
        Query: {query}
        Relevant Information:
        {documents}
        Provide a concise summary of the relevant information in the context of the query.
        """

        # Call Azure OpenAI GPT model for summarization
        response = azure_openai_client.chat.completions.create(
            model=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,  # Use the GPT deployment name
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and return the summary
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Azure OpenAI GPT summarization error: {e}")

# Streamlit App
st.title("Conversational RAG App")
st.write("Ask a question, and the app will retrieve relevant information from ChromaDB and summarize it for you.")

# Initialize session state for conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box for user query
if user_query := st.chat_input("Enter your query:"):
    # Add user message to conversation
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Process the query
    try:
        # Query ChromaDB
        results = query_chromadb(user_query)

        # Extract documents for summarization
        documents = "\n".join(results['documents'][0])

        # Summarize the results
        summary = summarize_results(user_query, documents)

        # Add assistant message to conversation
        with st.chat_message("assistant"):
            st.markdown(summary)
        st.session_state.messages.append({"role": "assistant", "content": summary})

        # Display retrieved chunks
        st.write("### Retrieved Chunks:")
        for i, (document, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            st.write(f"**Result {i + 1}:**")
            st.write(f"- **Metadata:** {metadata}")
            st.write(f"- **Document:\n** {document}")
    except Exception as e:
        st.error(f"An error occurred: {e}")