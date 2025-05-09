import pandas as pd
from dotenv import load_dotenv
import os
import chromadb
from chromadb import Client
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from tqdm import tqdm  # Import tqdm for progress bar

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI API configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "text-embedding-3-small")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

# Initialize Azure OpenAI client
azure_openai_client = AzureOpenAI(
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)

# # Initialize ChromaDB client
# chroma_client = Client(Settings(
#     persist_directory="./chromadb",  # Directory to store the database
#     chroma_db_impl="duckdb+parquet"
# ))

CHROMA_DATA_PATH = "./chromadb"  # Path to the ChromaDB data directory
chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

def load_excel_file():
    """
    Load the Excel file specified in the .env file.
    """
    # Get the file name from the .env file
    file_name = os.getenv("EXCEL_FILE_NAME")
    
    if not file_name:
        raise ValueError("EXCEL_FILE_NAME is not set in the .env file.")
    
    # Read the Excel file
    try:
        # data = pd.read_excel(file_name)
        data = pd.read_excel(file_name).head(10)

        return data  # Return the DataFrame
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_name}' was not found in the current folder.")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

def chunk_text(data, chunk_size=500):
    """
    Chunk the text data into smaller pieces for efficient retrieval.
    """
    combined_text = " ".join(data.astype(str).fillna("").apply(" ".join, axis=1))
    chunks = [combined_text[i:i+chunk_size] for i in range(0, len(combined_text), chunk_size)]
    return chunks

def embed_texts_azure(texts):
    """
    Generate embeddings for a list of texts using Azure OpenAI's API.
    """
    try:
        response = azure_openai_client.embeddings.create(
            input=texts,  # Pass the entire list of texts
            model=AZURE_OPENAI_DEPLOYMENT_NAME  # Use the deployment name as the engine
        )
        # Extract embeddings from the response
        embeddings = [item.embedding for item in response.data]
        return embeddings
    except Exception as e:
        raise Exception(f"Azure OpenAI API error: {e}")

def store_chunks_in_chromadb(chunks):
    """
    Store text chunks and their embeddings in ChromaDB.
    """
    # Create a collection in ChromaDB
    collection_name = "genie_text_metadata"

    # Check if the collection exists and delete it to reset
    if collection_name in chroma_client.list_collections():
        print(f"Collection '{collection_name}' exists. Resetting it...")
        chroma_client.delete_collection(name=collection_name)
        
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_functions.OpenAIEmbeddingFunction(
            api_key=AZURE_OPENAI_API_KEY,
            model_name=AZURE_OPENAI_DEPLOYMENT_NAME  # This is still used for compatibility with ChromaDB
        )
    )

    # Generate embeddings for all chunks at once
    print("Generating embeddings for all chunks...")
    embeddings = embed_texts_azure(chunks)

    # Add chunks and their embeddings to the collection
    print("Storing chunks and embeddings in ChromaDB...")
    for i, (chunk, embedding) in tqdm(enumerate(zip(chunks, embeddings))):
        collection.add(
            documents=[chunk],
            metadatas=[{"chunk_id": i}],
            ids=[f"chunk_{i}"],
            embeddings=[embedding]
        )
    print(f"Stored {len(chunks)} chunks in ChromaDB.")

if __name__ == "__main__":
    try:
        # Load the Excel file
        df = load_excel_file()
        print("File loaded successfully!")

        # Chunk the data
        chunks = chunk_text(df)
        print(f"Data chunked into {len(chunks)} pieces.")

        # Store chunks in ChromaDB
        store_chunks_in_chromadb(chunks)
        print("Chunks stored in ChromaDB successfully!")
    except Exception as e:
        print(e)