import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    room_id = "test_room"
    
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # Send join message with correct format
            join_message = json.dumps({
                "type": "join",
                "room_id": room_id  # Server expects 'room_id', not 'room'
            })
            await websocket.send(join_message)
            print(f"Sent join message for room {room_id}")
            
            # Wait for join confirmation
            response = await websocket.recv()
            try:
                data = json.loads(response)
                if data.get("type") == "join_confirm" and data.get("room_id") == room_id:
                    print(f"Successfully joined room: {room_id}")
                else:
                    print(f"Unexpected response: {data}")
                    return
            except json.JSONDecodeError:
                print("Invalid response format")
                return
            
            # Listen for messages
            while True:
                try:
                    message = await websocket.recv()
                    print(f"Received message: {message}")
                    
                    # Try to parse JSON
                    try:
                        data = json.loads(message)
                        print(f"Parsed JSON: {data}")
                        
                        # Handle server errors
                        if data.get("type") == "error":
                            print(f"Server error: {data.get('message', 'Unknown error')}")
                        
                    except json.JSONDecodeError:
                        print("Message is not JSON")
                        
                except websockets.ConnectionClosed:
                    print("Connection closed")
                    break
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket()) 