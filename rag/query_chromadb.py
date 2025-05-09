import os
from dotenv import load_dotenv
import chromadb
from chromadb import Client
from chromadb.config import Settings
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

# Initialize Azure OpenAI client
azure_openai_client = AzureOpenAI(
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)

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
    print("Generating embedding for the query...")
    query_embedding = embed_query_azure(query)

    # Retrieve the most relevant chunks from ChromaDB
    print("Querying ChromaDB for relevant chunks...")
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

if __name__ == "__main__":
    try:
        # Example query
        query = "What is the meaning of life?"
        print(f"Query: {query}")

        # Query ChromaDB
        results = query_chromadb(query)

        # Display results
        print("\nTop Results:")
        for i, (document, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"\nResult {i + 1}:")
            print(f"Document: {document}")
            print(f"Metadata: {metadata}")
    except Exception as e:
        print(e)