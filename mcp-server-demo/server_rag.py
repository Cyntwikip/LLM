# server.py
# from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP
import sys, requests, re, os
import pandas as pd
import xml.etree.ElementTree as ET

import chromadb
from chromadb.utils import embedding_functions
from openai import AzureOpenAI

from dotenv import load_dotenv

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


# Create an MCP server
# mcp = FastMCP("MCP Server with RAG", dependencies=["pandas", "numpy", "requests", "dotenv", "chromadb", "openai"]) # for STDIO
mcp = FastMCP("MCP Server with RAG")


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

def parse_log(log_text):
    """
    Parse the log text to extract timestamp, longitude, and latitude.
    :param log_text: Raw log text.
    :return: A DataFrame with parsed data.
    """
    # Define a regex pattern to extract timestamp, longitude, and latitude
    log_pattern = r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - .*GET .*lng=(?P<lng>[\d.]+)&lat=(?P<lat>[\d.]+)"
    
    # Find all matches in the log text
    matches = re.findall(log_pattern, log_text)
    
    # Convert matches to a DataFrame
    df = pd.DataFrame(matches, columns=["timestamp", "lng", "lat"])
    return df

@mcp.tool()
def get_travel_locations():
    """
    Fetch travel locations from the log file and parse them into a structured format.

    The function retrieves the log file from a predefined URL, parses the log text to extract
    timestamp, longitude, and latitude, and returns the data as a Pandas DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing the parsed travel locations with columns:
                      - "timestamp": The timestamp of the log entry.
                      - "lng": The longitude value.
                      - "lat": The latitude value.
                      Or a list with an error message if the logs cannot be fetched.
    """
    # Fetch the log file from the URL
    url = os.getenv('TRAVEL_LOCATIONS_URL')
    response = requests.get(url)
    if response.status_code != 200:
        return ["Error: Unable to fetch logs"]

    # Parse the log file
    log_text = response.text
    df = parse_log(log_text)

    return df

@mcp.tool()
def fetch_rss_feed():
    """
    Fetches an RSS feed from a ADB and parses it into a structured format.

    The function retrieves the RSS feed, parses the XML data, and extracts relevant fields 
    such as title, link, description, and publication date. The extracted data is returned 
    as a list of dictionaries.

    Returns:
        list[dict]: A list of dictionaries containing the RSS feed data with keys:
                    - "Title": The title of the RSS feed item.
                    - "Link": The URL link of the RSS feed item.
                    - "Description": The description of the RSS feed item.
                    - "Publication Date": The publication date of the RSS feed item.
    """
    feed_url = 'https://feeds.feedburner.com/adb_news'

    try:
        response = requests.get(feed_url)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        xml_data = response.content

        # Parse the XML data
        root = ET.fromstring(xml_data)
        items = root.findall(".//item")

        # Extract relevant fields
        feed_data = []
        for item in items:
            title = item.find("title").text if item.find("title") is not None else None
            link = item.find("link").text if item.find("link") is not None else None
            description = item.find("description").text if item.find("description") is not None else None
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else None

            feed_data.append({
                "Title": title,
                "Link": link,
                "Description": description,
                "Publication Date": pub_date
            })

        # # Create a Pandas DataFrame
        # df = pd.DataFrame(feed_data)
        # return df
        return feed_data

    except Exception as e:
        print(f"Error fetching RSS feed: {e}")
        return pd.DataFrame()
    
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


@mcp.tool()
def fetch_rag_data(query: str, top_k: int = 5):
    """
    Fetch and summarize relevant data from ChromaDB based on the user's query.

    Args:
        query (str): The user's query to search for relevant data.
        top_k (int): The number of top results to retrieve from ChromaDB.

    Returns:
        str: A summary of the relevant data retrieved from ChromaDB.
    """
    # Query ChromaDB for relevant chunks
    results = query_chromadb(query, top_k)

    # # Summarize the retrieved documents
    # summary = summarize_results(query, results)

    # results = query_chromadb(user_query)

    # # Extract documents for summarization
    # documents = "\n".join(results['documents'][0])

    # # Summarize the results
    # summary = summarize_results(user_query, documents)

    return results

# Start the server
if __name__ == "__main__":
    try:
        print("Debug: Starting MCP server...", file=sys.stderr)
        mcp.run(
            transport="streamable-http",
            host="127.0.0.1",
            port=8081,
            path="/mcp",
            log_level="debug",
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise