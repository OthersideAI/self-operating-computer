"""
Self-Operating Computer
"""
import argparse
import asyncio
from urllib.parse import urlparse
from utils.style import ANSI_BRIGHT_MAGENTA, ANSI_RED, ANSI_RESET
from operate import main
from utils.websocket_client import WebSocketClient
from models.prompts import get_system_prompt
from models.apis import get_next_action
from operate import operate


async def websocket_handler(websocket_uri: str, room_id: str, model: str, verbose_mode: bool):
    """Handle WebSocket connection and message processing."""
    async def message_handler(prompt: str):
        # Instead of awaiting main directly, we'll just call the operate function
        # since we're already in an async context
        try:
            system_prompt = get_system_prompt(model, prompt)
            system_message = {"role": "system", "content": system_prompt}
            messages = [system_message]
            operations, session_id = await get_next_action(model, messages, prompt, None)
            operate(operations, model)
        except Exception as e:
            print(f"{ANSI_RED}Error handling message: {e}{ANSI_RESET}")

    client = WebSocketClient(websocket_uri, room_id, message_handler)
    if await client.connect():
        try:
            await client.receive_messages()
        finally:
            await client.close()


def validate_websocket_uri(uri: str) -> bool:
    """Validate WebSocket URI format."""
    try:
        parsed = urlparse(uri)
        return parsed.scheme in ['ws', 'wss']
    except:
        return False


def main_entry():
    parser = argparse.ArgumentParser(
        description="Run the self-operating-computer with a specified model."
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Specify the model to use",
        required=False,
        default="gpt-4-with-ocr",
    )

    # Add a voice flag
    parser.add_argument(
        "--voice",
        help="Use voice input mode",
        action="store_true",
    )
    
    # Add a flag for verbose mode
    parser.add_argument(
        "--verbose",
        help="Run operate in verbose mode",
        action="store_true",
    )
    
    # Allow for direct input of prompt
    parser.add_argument(
        "--prompt",
        help="Directly input the objective prompt",
        type=str,
        required=False,
    )

    # WebSocket connection arguments
    parser.add_argument(
        "--websocket",
        help="WebSocket server URI (e.g., ws://localhost:8765)",
        type=str,
        required=False,
    )
    
    parser.add_argument(
        "--room",
        help="Room ID for WebSocket connection",
        type=str,
        required=False,
    )

    try:
        args = parser.parse_args()
        
        if args.websocket:
            # Validate WebSocket arguments
            if not validate_websocket_uri(args.websocket):
                print(f"{ANSI_RED}Error: Invalid WebSocket URI format. Must start with ws:// or wss://{ANSI_RESET}")
                return
                
            if not args.room:
                print(f"{ANSI_RED}Error: Room ID (--room) is required when using WebSocket mode{ANSI_RESET}")
                return
                
            # Run in WebSocket mode
            if args.voice:
                print(f"{ANSI_BRIGHT_MAGENTA}Warning: Voice mode is not supported with WebSocket mode{ANSI_RESET}")
            
            asyncio.run(websocket_handler(args.websocket, args.room, args.model, args.verbose))
        else:
            # Run in normal mode
            main(
                args.model,
                terminal_prompt=args.prompt,
                voice_mode=args.voice,
                verbose_mode=args.verbose
            )
    except KeyboardInterrupt:
        print(f"\n{ANSI_BRIGHT_MAGENTA}Exiting...")


if __name__ == "__main__":
    main_entry()
