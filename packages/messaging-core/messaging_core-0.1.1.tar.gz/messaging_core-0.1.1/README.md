# Messaging Core Python SDK

[![PyPI version](https://badge.fury.io/py/messaging-core.svg)](https://badge.fury.io/py/messaging-core)
[![Python Version](https://img.shields.io/pypi/pyversions/messaging-core.svg)](https://pypi.org/project/messaging-core/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python gRPC client for the Messaging Core service, providing easy access to messaging functionality including user management, conversations, and real-time messaging.

## Installation

### Prerequisites

- Python 3.8 or higher
- gRPC and Protocol Buffers support

### Install from PyPI

```bash
pip install messaging-core
```

## Quick Start

### Basic Usage

```python
from messaging_core import MessagingCoreClient

# Initialize the client with your server address and API key
client = MessagingCoreClient(
    server_address="your-server-address:50051",  # e.g., "localhost:50051"
    api_key="your-api-key-here",
    use_ssl=False  # Set to True in production
)

# Login with user credentials
try:
    auth_response = client.login(
        username="user@example.com",
        password="your-secure-password"
    )
    print(f"Successfully logged in as {auth_response.user.email}")
    
    # Get user conversations
    conversations = client.list_conversations()
    print(f"Found {len(conversations)} conversations")
    
    # Send a message
    message = client.send_message(
        conversation_id=conversations[0].id,
        content="Hello from Python SDK!"
    )
    print(f"Message sent with ID: {message.id}")
    
except Exception as e:
    print(f"Error: {e}")
```

## Features

- **Authentication**: Secure login with JWT tokens
- **Conversation Management**: Create, list, and manage conversations
- **Messaging**: Send and receive messages in real-time
- **User Management**: User profiles and presence
- **Attachments**: Send and receive files and media

## API Reference

### Initialization

```python
from messaging_core import MessagingCoreClient

# For development (without SSL)
client = MessagingCoreClient(
    server_address="localhost:50051",
    api_key="your-api-key",
    use_ssl=False
)

# For production (with SSL)
client = MessagingCoreClient(
    server_address="api.yourdomain.com:443",
    api_key="your-api-key",
    use_ssl=True
)
```

### Authentication

```python
# Login with username/password
auth_response = client.login(
    username="user@example.com",
    password="your-password"
)

# The client automatically handles token refresh
# You can also manually refresh the token
new_tokens = client.refresh_token(
    refresh_token=auth_response.refresh_token
)

# Logout
client.logout()
```

### Conversations

```python
# List conversations with pagination
conversations = client.list_conversations(
    page=1,
    page_size=20
)

# Create a new conversation
conversation = client.create_conversation(
    title="Team Chat",
    participant_ids=["user1", "user2"],
    type="GROUP"
)

# Get conversation details
conversation = client.get_conversation(conversation_id="conv123")

# Delete a conversation
client.delete_conversation(conversation_id="conv123")
```

### Messages

```python
# Send a text message
message = client.send_message(
    conversation_id="conv123",
    content="Hello, world!"
)

# Send a message with metadata
message = client.send_message(
    conversation_id="conv123",
    content="Check this out!",
    metadata={"type": "announcement", "priority": "high"}
)

# Get message history
messages = client.get_messages(
    conversation_id="conv123",
    limit=50,
    before=datetime.utcnow()
)
```

### Users

```python
# Get current user profile
profile = client.get_my_profile()

# Update profile
updated = client.update_profile(
    first_name="John",
    last_name="Doe",
    avatar_url="https://example.com/avatar.jpg"
)

# Search users
users = client.search_users(query="john")
```

## Error Handling

All API calls raise `grpc.RpcError` for gRPC-related errors. The client also provides custom exceptions for business logic errors.

```python
try:
    client.login(username="user@example.com", password="wrong-password")
except Exception as e:
    if hasattr(e, 'code') and e.code() == grpc.StatusCode.UNAUTHENTICATED:
        print("Authentication failed: Invalid credentials")
    else:
        print(f"Error: {e}")
```

## Development

For development and contributing, you'll need:

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/alijkdkar/Messaging-Core.git
   cd Messaging-Core/docs/sdk/python
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

### Generating gRPC Code

To regenerate the gRPC code from the .proto files:

```bash
./scripts/generate_sdk.sh
```

### Running Tests

```bash
pytest tests/
```

### Building the Package

```bash
python -m build
```

### Publishing to PyPI

1. Build the package:
   ```bash
   python -m build
   ```

2. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
