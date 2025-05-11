### Basic MCP Tutorial with RAG

This tutorial provides a step-by-step guide to set up and run a basic MCP (Model Context Protocol) server with Retrieval-Augmented Generation (RAG) using the `FastMCP` library.

---

### Prerequisites

- **Python 3.11 or higher** installed on your system.
- **`pip`** (Python package manager) installed.

---

### Setup Instructions

#### 1. **Initialize a Virtual Environment**
To keep your project dependencies isolated, create and activate a virtual environment using `uv` (or `venv`).

```bash
# Initialize a virtual environment
uv init

# Create a virtual environment named 'venv'
uv venv

# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
.venv\Scripts\activate     # On Windows
```

#### 2. **Install Dependencies**
Install the required libraries using `pip`:

```bash
uv pip install fastmcp chromadb azure-ai-openai python-dotenv pandas numpy requests
```

---

### Running the MCP Server with RAG

#### 1. **Configure Environment Variables**
Create a `.env` file in the same directory as `server_rag.py` and add the following environment variables:

```env
AZURE_OPENAI_ENDPOINT=https://<your-resource-name>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment-name>
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=<your-chat-deployment-name>
```

Replace `<your-resource-name>`, `<your-api-key>`, and `<your-deployment-name>` with your Azure OpenAI configuration details.

#### 2. **Start the Server**
Run the `server_rag.py` script to start the MCP server with RAG capabilities:

```bash
python server_rag.py
```

You should see output similar to:
```
INFO:     Uvicorn running on http://127.0.0.1:8081 (Press CTRL+C to quit)
```

---

### Running the MCP Client

#### 1. **Create the Client Script**
Ensure you have a client.py script to interact with the server.

#### 2. **Run the Client**
Run the client script to interact with the server:
```bash
python client.py
```

Expected Output:
```
Pinging server...
Server is reachable!

Testing resource: greeting://{name}
Resource response: Resource echo: Hello, Jude, MCP!

Testing tool: get_travel_locations
Tool response: ...

Testing tool: fetch_rss_feed
Tool response: ...

Testing tool: fetch_rag_data
Tool response: ...
```

---

### Additional Notes

#### 1. **Testing Remote Access**
To make the server accessible remotely, update the `host` parameter in `server_rag.py` to `0.0.0.0`:
```python
host="0.0.0.0"
```

#### 2. **Using a Different Port**
You can change the port by modifying the `port` parameter in `server_rag.py`:
```python
port=9000
```

#### 3. **Stopping the Server**
To stop the server, press `CTRL+C` in the terminal where the server is running.

---

### Troubleshooting

- **Port Already in Use**:
  If the server fails to start due to a port conflict, free the port by running:
  ```bash
  kill -9 $(lsof -t -i:8081)
  ```

- **Dependencies Not Found**:
  Ensure the virtual environment is activated before running the scripts:
  ```bash
  source .venv/bin/activate  # On macOS/Linux
  .venv\Scripts\activate     # On Windows
  ```

---

### Summary

This tutorial covered:
- Setting up a virtual environment.
- Installing dependencies for `server_rag.py`.
- Creating and running an MCP server with RAG capabilities.
- Interacting with the server using a client script.

Feel free to extend the server with additional tools, resources, and prompts to suit your needs!