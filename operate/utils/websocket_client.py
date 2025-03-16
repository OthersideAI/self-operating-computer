import asyncio
import json
import websockets
from typing import Optional, Callable
from utils.style import ANSI_GREEN, ANSI_RED, ANSI_RESET, ANSI_YELLOW

class WebSocketClient:
    def __init__(self, uri: str, room_id: str, message_handler: Callable):
        self.uri = uri
        self.room_id = room_id
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.message_handler = message_handler
        self.running = False

    async def join_room(self):
        """Send join room message and initial status."""
        if not self.websocket:
            return False
        
        try:
            # Send join message with correct format
            print(f"{ANSI_YELLOW}Joining room {self.room_id}...{ANSI_RESET}")
            join_message = json.dumps({
                "type": "join",
                "room_id": self.room_id  # Server expects 'room_id', not 'room'
            })
            await self.websocket.send(join_message)
            
            # Wait for join confirmation
            response = await self.websocket.recv()
            try:
                data = json.loads(response)
                if data.get("type") == "join_confirm" and data.get("room_id") == self.room_id:
                    print(f"{ANSI_GREEN}Successfully joined room: {self.room_id}{ANSI_RESET}")
                    
                    # Send initial status message
                    status_message = json.dumps({
                        "type": "status",
                        "room_id": self.room_id,  # Server expects 'room_id'
                        "status": "connected",
                        "client_type": "self_operating_computer"
                    })
                    await self.websocket.send(status_message)
                    return True
                else:
                    print(f"{ANSI_RED}Failed to join room: Unexpected response - {data}{ANSI_RESET}")
                    return False
            except json.JSONDecodeError:
                print(f"{ANSI_RED}Failed to join room: Invalid response format{ANSI_RESET}")
                return False
                
        except Exception as e:
            print(f"{ANSI_RED}Failed to join room: {e}{ANSI_RESET}")
            return False

    async def connect(self):
        """Establish WebSocket connection and join room."""
        try:
            print(f"{ANSI_YELLOW}Connecting to WebSocket server at {self.uri}...{ANSI_RESET}")
            # Add /ws to the URI if not present
            uri = self.uri if self.uri.endswith('/ws') else f"{self.uri}/ws"
            self.websocket = await websockets.connect(uri)
            print(f"{ANSI_GREEN}Connected to WebSocket server{ANSI_RESET}")
            
            # Join room after connection
            if await self.join_room():
                self.running = True
                return True
            else:
                await self.close()
                return False
                
        except websockets.exceptions.InvalidStatusCode as e:
            print(f"{ANSI_RED}Failed to connect to WebSocket server: Invalid status code {e.status_code}{ANSI_RESET}")
            return False
        except Exception as e:
            print(f"{ANSI_RED}Failed to connect to WebSocket server: {str(e)}{ANSI_RESET}")
            return False

    async def receive_messages(self):
        """Listen for messages and handle them."""
        while self.running and self.websocket:
            try:
                message = await self.websocket.recv()
                print(f"{ANSI_YELLOW}Received message: {message}{ANSI_RESET}")
                
                # Try to parse as JSON first
                try:
                    data = json.loads(message)
                    
                    # Handle different message formats
                    if isinstance(data, dict):
                        # Look for prompt in various fields
                        prompt = None
                        for field in ['content', 'prompt', 'message', 'text', 'command']:
                            if field in data:
                                prompt = data[field]
                                break
                        
                        # If found prompt, handle it
                        if prompt:
                            await self.message_handler(prompt)
                        # If no prompt found but message has type field
                        elif 'type' in data:
                            msg_type = data['type']
                            if msg_type == 'ping':
                                await self.websocket.send(json.dumps({
                                    "type": "pong",
                                    "room_id": self.room_id  # Server expects 'room_id'
                                }))
                            elif msg_type == 'error':
                                print(f"{ANSI_RED}Server error: {data.get('message', 'Unknown error')}{ANSI_RESET}")
                    
                except json.JSONDecodeError:
                    # If not JSON, treat as raw prompt
                    await self.message_handler(message)
                    
            except websockets.ConnectionClosed:
                print(f"{ANSI_RED}WebSocket connection closed{ANSI_RESET}")
                self.running = False
                # Try to reconnect
                if await self.connect():
                    continue
                break
            except Exception as e:
                print(f"{ANSI_RED}Error receiving message: {e}{ANSI_RESET}")

    async def close(self):
        """Close the WebSocket connection."""
        self.running = False
        if self.websocket:
            try:
                # Send disconnect message
                await self.websocket.send(json.dumps({
                    "type": "status",
                    "room_id": self.room_id,  # Server expects 'room_id'
                    "status": "disconnected"
                }))
            except:
                pass  # Ignore errors during disconnect message
            await self.websocket.close()
            self.websocket = None 