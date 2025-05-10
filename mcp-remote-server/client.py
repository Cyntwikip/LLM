import asyncio
from fastmcp import Client

SERVER_URL = "http://127.0.0.1:8080/mcp"

async def example():
    async with Client(SERVER_URL) as client:
        await client.ping()

async def test_server():
    # Connect to the MCP server
    async with Client(SERVER_URL) as client:

        # Test resource: echo://{message}
        print("\nTesting resource: echo://{message}")
        response = await client.read_resource("echo://Hello,%20MCP!")
        print(f"Resource response: {response}")

        # Test tool: echo_tool
        print("\nTesting tool: echo_tool")
        response = await client.call_tool("echo_tool", {"message": "Hello, Tool!"})
        print(f"Tool response: {response}")

        # Test prompt: echo_prompt
        print("\nTesting prompt: echo_prompt")
        response = await client.get_prompt("echo_prompt", {"message": "Hello, Prompt!"})
        print(f"Prompt response: {response}")

if __name__ == "__main__":
    asyncio.run(example())
    asyncio.run(test_server())