# Pyrubi Modern

A modern, asynchronous, and performant Python library for interacting with the Rubika API.

## Features

*   **Asynchronous:** Built from the ground up using `asyncio` for non-blocking operations and high concurrency.
*   **Type-hinted:** Fully type-hinted codebase for improved readability, maintainability, and IDE support.
*   **Pydantic Models:** Uses Pydantic for robust data validation and serialization of API objects.
*   **Modular Design:** Clear separation of concerns for network, API methods, client logic, and session management.
*   **Comprehensive Error Handling:** Custom exceptions for network issues, authentication failures, and API errors.
*   **Session Management:** Automatic saving and loading of session data for persistent connections.

## Installation

To install `pyrubi-modern`, you can use `pip`:

```bash
pip install pyrubi-modern
```

Alternatively, if you are using `Poetry` (recommended for development):

```bash
poetry add pyrubi-modern
```

## Quick Start

Here's a quick example of how to use `pyrubi-modern` to create a simple bot that echoes messages:

```python
import asyncio
from pyrubi_modern import Client, AuthData
from pyrubi_modern.types.models import Message

async def main():
    # Replace with your actual authentication data
    # You can obtain auth_key and private_key through Rubika's login process
    # or by migrating from an existing session.
    auth_data = AuthData(
        auth_key="YOUR_AUTH_KEY",
        private_key="YOUR_PRIVATE_KEY",
    )

    client = Client(session_name="my_rubika_bot", auth_data=auth_data)

    @client.on_message
    async def echo_handler(message: Message):
        print(f"Received message from {message.sender_id} in {message.chat_id}: {message.text}")
        if message.text and message.text.lower() == "hello":
            await client.api.send_text_message(message.chat_id, f"Hello, {message.sender_id}!")

    print("Starting client...")
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Manual Session Login

If you don't have `auth_key` and `private_key` directly, you might need to perform a login flow. The `login` method is a placeholder and would need to be implemented based on Rubika's specific authentication process.

```python
import asyncio
from pyrubi_modern import Client

async def login_example():
    client = Client(session_name="my_new_session")
    # This is a placeholder. Real Rubika login might involve more steps (e.g., sending phone number, receiving code).
    # You would typically get auth_key and private_key from a successful login response.
    # For demonstration, let's assume you get them from environment variables or a secure config.
    
    # Example: In a real scenario, you'd call an API method to initiate login
    # and then another to confirm with a code, receiving auth_key and private_key.
    # For now, we'll simulate it.
    
    # await client.login("obtained_auth_key", "obtained_private_key")
    print("Please implement actual Rubika login flow to obtain auth_key and private_key.")
    print("Once obtained, you can use client.login(auth_key, private_key) to save the session.")

if __name__ == "__main__":
    asyncio.run(login_example())
```

## API Reference

The `Client` object exposes an `api` attribute which contains methods for interacting with the Rubika API.

### `Client.api.get_me() -> User`

Retrieves information about the current authenticated user.

```python
user = await client.api.get_me()
print(f"Logged in as: {user.username or user.first_name}")
```

### `Client.api.send_text_message(chat_id: str, text: str, reply_to_message_id: Optional[str] = None) -> Message`

Sends a text message to a specified chat.

*   `chat_id`: The GUID of the target chat.
*   `text`: The content of the message.
*   `reply_to_message_id`: (Optional) The ID of the message to reply to.

```python
sent_message = await client.api.send_text_message("g0B123456789abcdef", "Hello from pyrubi-modern!")
print(f"Message sent with ID: {sent_message.message_id}")
```

### `Client.api.get_chat_history(chat_id: str, limit: int = 20, offset_id: Optional[str] = None) -> List[Message]`

Retrieves a list of messages from a chat's history.

*   `chat_id`: The GUID of the target chat.
*   `limit`: (Optional) Maximum number of messages to retrieve (default: 20).
*   `offset_id`: (Optional) The ID of the message to start retrieving history from.

```python
history = await client.api.get_chat_history("g0B123456789abcdef", limit=5)
for msg in history:
    print(f"- {msg.sender_id}: {msg.text}")
```

### `Client.api.get_chats() -> List[Chat]`

Retrieves a list of all chats the user is part of.

```python
chats = await client.api.get_chats()
for chat in chats:
    print(f"- Chat: {chat.title} (Type: {chat.type})")
```

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests on the [GitHub repository](https://github.com/YOUR_GITHUB_USERNAME/pyrubi-modern).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References

[1] [pyrubi · PyPI](https://pypi.org/project/pyrubi/)
[2] [GitHub - AliGanji1/Pyrubi: Pyrubi is a powerful library for building self robots in Rubika](https://github.com/AliGanji1/Pyrubi)

