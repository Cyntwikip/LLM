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

---

## Debugging Guide for MCP Server with Streamlit

This section provides a step-by-step guide to enable debugging for your Streamlit application (`rag_chat_app.py`) using the Python Debugger in Visual Studio Code.

---

### Prerequisites

1. **Install the Python Extension**:
   - Open Visual Studio Code.
   - Go to the Extensions view (`Ctrl+Shift+X` or `Cmd+Shift+X` on macOS).
   - Search for and install the **Python** extension by Microsoft.

2. **Ensure Your Virtual Environment is Set Up**:
   - Activate your virtual environment:
     ```bash
     source .venv/bin/activate  # On macOS/Linux
     .venv\Scripts\activate     # On Windows
     ```

---

### Setting Up Debugging in VS Code

1. **Create or Update `launch.json`**:
   - Open the **Run and Debug** panel (`Ctrl+Shift+D` or `Cmd+Shift+D` on macOS).
   - Click **"Create a launch.json file"** if you don’t already have one.
   - Add the following configuration to your `launch.json` file:

   ```jsonc
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Streamlit: Debug Current File",
               "type": "python",
               "request": "launch",
               "cwd": "${workspaceFolder}/LLM Materials/LLM/mcp-server-demo", // Set working directory to the folder with .env
               "env": {
                   "PYTHONPATH": "${workspaceFolder}/LLM Materials/LLM/mcp-server-demo/.venv/bin"
               },
               "pythonPath": "${workspaceFolder}/LLM Materials/LLM/mcp-server-demo/.venv/bin/python", // Explicitly set Python interpreter
               "program": "${workspaceFolder}/LLM Materials/LLM/mcp-server-demo/.venv/bin/streamlit", // Path to Streamlit in .venv
               "args": [
                   "run",
                   "${file}"
               ],
               "console": "integratedTerminal",
               "justMyCode": false
           }
       ]
   }
   ```

2. **Explanation of Configuration**:
   - **`cwd`**: Sets the working directory to the folder containing your `.env` file.
   - **`env`**: Ensures the `PYTHONPATH` includes the `.venv` folder.
   - **`pythonPath`**: Explicitly points to the Python interpreter in your `.venv`.
   - **`program`**: Specifies the `streamlit` executable inside your `.venv`.
   - **`args`**: Passes the `run` command and the currently open file (`${file}`) to Streamlit.

---

### Running the Debugger

1. **Open the File**:
   - Open `rag_chat_app.py` in Visual Studio Code.

2. **Set Breakpoints**:
   - Click to the left of the line numbers to set breakpoints where you want to pause execution.

3. **Select the Debug Configuration**:
   - Go to the **Run and Debug** panel.
   - Select **"Streamlit: Debug Current File"** from the dropdown.

4. **Start Debugging**:
   - Press **F5** or click the green "Run" button to start debugging.

5. **Inspect Variables and Step Through Code**:
   - Use the **Debug Console** to inspect variables.
   - Use the **Step Over (F10)**, **Step Into (F11)**, and **Continue (F5)** buttons to navigate through the code.

---

### Notes

- **Ensure the Correct File is Selected**:
  - Make sure `rag_chat_app.py` is the active file when running the debugger.

- **Restart VS Code if Necessary**:
  - If the debugger doesn’t work as expected, restart VS Code to apply the changes.

- **Verify the Python Interpreter**:
  - Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P` on macOS).
  - Search for **"Python: Select Interpreter"** and ensure the interpreter points to your `.venv`.

---

### Example Debugging Workflow

1. Set a breakpoint at the following line in `rag_chat_app.py`:
   ```python
   print("CURRENT DIRECTORY:", os.getcwd())
   ```

2. Start the debugger and observe the output in the **Debug Console**.

3. Step through the code to inspect the values of variables like `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY`.

4. Use the **Debug Console** to execute commands and test variable values.

---