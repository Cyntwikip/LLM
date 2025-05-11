import asyncio
from fastmcp import Client

SERVER_URL = "http://127.0.0.1:8081/mcp"

async def test_server():
    # Connect to the MCP server
    async with Client(SERVER_URL) as client:

         # Test server ping
        print("Pinging server...")
        await client.ping()
        print("Server is reachable!")

        # Test resource: greeting://{name}
        print("\nTesting resource: greeting://{name}")
        response = await client.read_resource("greeting://Jude,%20MCP!")
        print(f"Resource response: {response}")

        # Test tool: get_travel_locations
        print("\nTesting tool: get_travel_locations")
        response = await client.call_tool("get_travel_locations", {})
        print(f"Tool response: {response}")

        # Test tool: fetch_rss_feed
        print("\nTesting tool: fetch_rss_feed")
        response = await client.call_tool("fetch_rss_feed", {})
        print(f"Tool response: {response}")

        # Test tool: fetch_rss_feed
        print("\nTesting tool: fetch_rag_data")
        response = await client.call_tool("fetch_rag_data", {"query": "What are the main insights?", "top_k": 5})
        print(f"Tool response: {response}")

if __name__ == "__main__":
    asyncio.run(test_server())