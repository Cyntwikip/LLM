# server.py
from mcp.server.fastmcp import FastMCP
import sys, requests, re, os
import pandas as pd
import xml.etree.ElementTree as ET

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create an MCP server
mcp = FastMCP("Demo", dependencies=["pandas", "numpy", "requests", "dotenv"])

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


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

        # Create a Pandas DataFrame
        df = pd.DataFrame(feed_data)
        return df

    except Exception as e:
        print(f"Error fetching RSS feed: {e}")
        return pd.DataFrame()

# Start the server
if __name__ == "__main__":
    try:
        print("Debug: Starting MCP server...", file=sys.stderr)
        mcp.run()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise