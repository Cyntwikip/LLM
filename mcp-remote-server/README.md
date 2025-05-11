## Basic MCP Tutorial

This tutorial provides a step-by-step guide to set up and run a basic MCP (Model Context Protocol) server and client using the `FastMCP` library.

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
Install the `FastMCP` library using `pip`:

```bash
uv pip install fastmcp
```

---

### Running the MCP Server

Start the server by running the following command:
```bash
python server.py
```

You should see output similar to:
```
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
```

---

### Running the MCP Client

Run the client script to interact with the server:
```bash
python client.py
```

Expected Output:
```
Resource Response: Resource echo: Hello
Tool Response: Tool echo: Hello
Prompt Response: Please process this message: Hello
```

---

### Additional Notes

#### 1. **Testing Remote Access**
To make the server accessible remotely, update the `host` parameter in `server.py` to `0.0.0.0`:
```python
host="0.0.0.0"
```

#### 2. **Using a Different Port**
You can change the port by modifying the `port` parameter in `server.py`:
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
  kill -9 $(lsof -t -i:8080)
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
- Installing `FastMCP`.
- Creating and running an MCP server.
- Interacting with the server using a client script.

Feel free to extend the server with additional tools, resources, and prompts to suit your needs!

