import streamlit as st
import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
import openai
from openai import AzureOpenAI

import asyncio
from fastmcp import Client

print("CURRENT DIRECTORY:", os.getcwd())

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI API configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

print('Python openai version:', openai.__version__)

# Initialize Azure OpenAI client
azure_openai_client = AzureOpenAI(
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)

MAX_HISTORY_LENGTH = 10

if "message_history" not in st.session_state:
    st.session_state.message_history = []  

# MCP server URL
SERVER_URL = "http://127.0.0.1:8081/mcp"

async def connect_server():
    # Connect to the MCP server
    async with Client(SERVER_URL) as client:

        tools = await client.list_tools()
        # print(tools)
        print("\nConnected to server with tools:", [tool.name for tool in tools])

        return client
    
def convert_mcp_tools_to_openai_format(tools):
    available_tools = [{
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
            "type": "object",
            "properties": {
                key: {
                "type": value.get("type", "string"),
                "title": value.get("title", key),
                **({"default": value["default"]} if "default" in value else {})
                }
                for key, value in tool.inputSchema["properties"].items()
            },
            "required": tool.inputSchema.get("required", [])
            }
        }
        } for tool in tools]
    
    return available_tools
    

async def process_query(query: str) -> str:
    """Process a query using Azure OpenAI and available tools from the MCP server."""

    async with Client(SERVER_URL) as client:
        print('---Connected to server---')

        # List available tools from the MCP server
        tools = await client.list_tools()
        print("\nConnected to server with tools:", [tool.name for tool in tools])

        available_tools = convert_mcp_tools_to_openai_format(tools)

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]

        messages = st.session_state.message_history + messages
        messages = messages[-MAX_HISTORY_LENGTH:]

        past_tool_choices = []

        try:
            while True:
                filtered_available_tools = [i for i in available_tools 
                                if i['function']['name'] not in past_tool_choices]

                # Call Azure OpenAI for text completion
                response = azure_openai_client.chat.completions.create(
                    model=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7,
                    tools=filtered_available_tools,
                    tool_choice="auto"
                )

                print('---Azure OpenAI response---')

                if response.choices[0].finish_reason == "stop":
                    # Extract the assistant's response
                    final_text = response.choices[0].message.content
                    messages.append({"role": "assistant", "content": final_text})

                    st.session_state.message_history = messages
                    return final_text

                elif response.choices[0].finish_reason == "tool_calls":
                    # Extract the tool call details
                    content = response.choices[0].message.tool_calls[0]
                    tool_choice = content.function.name
                    print('Tool choice:', tool_choice)
                    past_tool_choices.append(tool_choice)

                    # Find the tool and execute it
                    for tool in filtered_available_tools:
                        if tool['function']['name'] == tool_choice:
                            tool_name = tool['function']['name']
                            tool_args = eval(content.function.arguments)

                            # Execute the tool call
                            tool_result = await client.call_tool(tool_name, tool_args)
                            tool_result = tool_result[0].text

                            # Append the tool result to the conversation
                            messages.append({"role": "system", "content": tool_result})
                            break
                else:
                    # Handle other finish reasons if necessary
                    return "No valid response from Azure OpenAI."

        except Exception as e:
            print(e)
            raise Exception(f"Error during Azure OpenAI completion or tool execution: {e}")

# Streamlit App
st.title("Conversational RAG App with MCP Server")
st.write("Ask a question, and the app will retrieve relevant information from the MCP server.")

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
        # Call the asynchronous process_query function
        output = asyncio.run(process_query(user_query))  # Use asyncio.run to handle the async function
        # print('---Processed query---')

        # Add assistant message to conversation
        with st.chat_message("assistant"):
            st.markdown(output)
        st.session_state.messages.append({"role": "assistant", "content": output})

    except Exception as e:
        st.error(f"An error occurred: {e}")