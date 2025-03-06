import asyncio
import websockets
import json

payload = {
    "tool": "generate_image",
    "params": json.dumps({"prompt": "a dog wearing sunglasses", "width": 512, "height": 512})
}

async def test_mcp_server():
    uri = "ws://localhost:9000"
    try:
        async with websockets.connect(uri) as ws:
            print("Connected to MCP server")
            await ws.send(json.dumps(payload))
            response = await ws.recv()
            print("Response from server:")
            print(json.dumps(json.loads(response), indent=2))
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    print("Testing MCP server with WebSocket...")
    asyncio.run(test_mcp_server())