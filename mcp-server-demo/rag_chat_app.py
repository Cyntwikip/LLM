import streamlit as st
import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
import openai
from openai import AzureOpenAI

import asyncio
from fastmcp import Client

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

# MCP server URL
SERVER_URL = "http://127.0.0.1:8081/mcp"

async def connect_server():
    # Connect to the MCP server
    async with Client(SERVER_URL) as client:

        tools = await client.list_tools()
        # print(tools)
        print("\nConnected to server with tools:", [tool.name for tool in tools])

        return client
    

async def process_query(query: str) -> str:
    """Process a query using Azure OpenAI and available tools from the MCP server."""
    # Connect to the MCP server
    # await connect_server()
    # print('---Test done---')

    async with Client(SERVER_URL) as client:
        print('---Connected to server---')

        # List available tools from the MCP server
        tools = await client.list_tools()
        print("\nConnected to server with tools:", [tool.name for tool in tools])
        # print(tools)

        # available_tools = [{
        #     "name": tool.name,
        #     "description": tool.description,
        #     "parameters": tool.inputSchema
        # } for tool in tools]

        # print("\nConnected to server with tools:", [tool.name for tool in available_tools])

        # available_tools = [{
        #                         "type": "function",
        #                         "function": tool
        #                     } for tool in tools]

        available_tools = [{
            "type": "function",  # The type of the tool (e.g., "function")
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",  # The type of the input schema (e.g., "object")
                    "properties": {
                        key: {
                            "type": value.get("type", "string"),  # Default to "string" if type is not specified
                            "title": value.get("title", key),    # Use the key as the title if not specified
                            **({"default": value["default"]} if "default" in value else {})  # Include default only if it exists
                        }
                        for key, value in tool.inputSchema["properties"].items()
                    },
                    "required": tool.inputSchema.get("required", [])  # Include required fields
                }
            }
        } for tool in tools]
        
        # print('Available tools:')
        # print(available_tools)

        # Prepare the initial messages for Azure OpenAI
        # messages = [
        #     {
        #         "role": "user",
        #         "content": query
        #     }
        # ]

        messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ]

        # Call Azure OpenAI for text completion
        try:
            response = azure_openai_client.chat.completions.create(
                model=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,  # Use the GPT deployment name
                messages=messages,
                max_tokens=1000,
                temperature=0.7, 
                tools=available_tools,  # Pass the available tools to the model
                tool_choice="auto"  # Let the model choose the tool
            )

            print('---Azure OpenAI response---')
            print(response)

            final_text = None

            if response.choices[0].finish_reason == "stop":

                print('---Stop reason---')

                # Extract the assistant's response
                assistant_response = response.choices[0].message.content
                print(assistant_response)
                # final_text = [assistant_response]
                final_text = assistant_response

            elif response.choices[0].finish_reason == "tool_calls":

                print('---Tool calls reason---')
                # print(response.choices[0].message.tool_calls[0])

                content = response.choices[0].message.tool_calls[0]
                # print(content)
                # print(dict(content.function)['name'])
                # assistant_response = dict(content.function)['name']
                tool_choice = content.function.name
                # print(tool_choice)

                # Process tool calls if required
                for tool in available_tools:

                    # if tool.name in tool_choice:
                    if tool['function']['name'] == tool_choice:
                        # tool_name = tool.name
                        tool_name = tool['function']['name']
                        # tool_args = {}  # Extract arguments from the assistant's response if needed
                        # print('converting tool args')
                        # tool_args = dict(content.function.arguments)
                        
                        # print('converting tool args success')

                        # tool_args = tool['function']['parameters']['properties']   
                        # tool_args = dict(dict(content.function).arguments)
                        tool_args = eval(content.function.arguments)
                        # print(tool_args)

                        # Execute the tool call
                        tool_result = await client.call_tool(tool_name, tool_args)
                        # print(tool_result)
                        # print(len(tool_result))
                        # final_text.append(f"[Tool {tool_name} executed with result: {tool_result}]")
                        tool_result = tool_result[0].text
                        # print(tool_result)

                        messages.append(
                            {
                                "role": "user",
                                "content": tool_result
                                
                                # TODO: below is not working. maybe version issue
                                # "content": [
                                #                 {
                                #                     "type": "tool_result",
                                #                     "tool_use_id": content.id,
                                #                     # "content": tool_result
                                #                     "content": 'dummy message'
                                #                 }
                                #             ]
                            }
                        )

                        response = azure_openai_client.chat.completions.create(
                                        model=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,  # Use the GPT deployment name
                                        max_tokens=1000,
                                        temperature=0.7, 
                                        messages=messages
                                    )

                        # final_text.append(response.choices[0].message.content)
                        final_text = response.choices[0].message.content

                        break

            else:
                # Handle other finish reasons if necessary
                # final_text = ["No valid response from Azure OpenAI."]
                final_text = "No valid response from Azure OpenAI."

            # return "\n".join(final_text)
            return final_text

        except Exception as e:
            print(e)
            raise Exception(f"Error during Azure OpenAI completion or tool execution: {e}")

# def summarize_results(query, documents):
#     """
#     Summarize the retrieved documents in the context of the query using Azure OpenAI's GPT model.
#     """
#     try:
#         # Prepare the prompt for summarization
#         prompt = f"""
#         You are an assistant that summarizes information in the context of a user's query.
#         Query: {query}
#         Relevant Information:
#         {documents}
#         Provide a concise summary of the relevant information in the context of the query.
#         """

#         # Call Azure OpenAI GPT model for summarization
#         response = azure_openai_client.chat.completions.create(
#             model=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,  # Use the GPT deployment name
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": prompt}
#             ]
#         )

#         # Extract and return the summary
#         return response.choices[0].message.content
#     except Exception as e:
#         raise Exception(f"Azure OpenAI GPT summarization error: {e}")

# print('TEST')

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