# Backboard Python SDK

A developer-friendly Python SDK for the Backboard API. Build conversational AI applications with persistent memory and intelligent document processing.

## ✨ New in v1.0.3

- **Simplified Tool Definitions**: Use plain JSON objects instead of verbose SDK classes
- **Enhanced Tool Call Handling**: Object-oriented access with automatic JSON parsing
- **Simplified Tool Outputs**: Use plain dictionaries for tool results
- **Improved Developer Experience**: Less boilerplate, more intuitive APIs

## Installation

```bash
pip install backboard-sdk
```

Or install from source:

```bash
git clone https://github.com/backboard/backboard-python-sdk.git
cd backboard-python-sdk
pip install -e .
```

## Quick Start

```python
from backboard import BackboardClient

# Initialize the client
client = BackboardClient(api_key="your_api_key_here")

# Create an assistant
assistant = client.create_assistant(
    name="Support Bot",
    description="A helpful customer support assistant"
)

# Create a conversation thread
thread = client.create_thread(assistant.assistant_id)

# Send a message
response = client.add_message(
    thread_id=thread.thread_id,
    content="Hello! Can you help me with my account?"
)

print(response.latest_message.content)
```

## Features

### Assistants
- Create, list, get, update, and delete assistants
- Configure custom tools and capabilities
- Upload documents for assistant-level context

### Threads
- Create conversation threads under assistants
- Maintain persistent conversation history
- Support for message attachments

### Documents
- Upload documents to assistants or threads
- Automatic processing and indexing for RAG
- Support for PDF, Office files, text, and more
- Real-time processing status tracking

### Messages
- Send messages with optional file attachments
- Streaming and non-streaming responses
- Tool calling support
- Custom LLM provider and model selection

## API Reference

### Client Initialization

```python
client = BackboardClient(api_key="your_api_key")
```

### Assistants

```python
# Create assistant
assistant = client.create_assistant(
    name="My Assistant",
    description="Assistant description",
    tools=[tool_definition]  # Optional
)

# List assistants
assistants = client.list_assistants(skip=0, limit=100)

# Get assistant
assistant = client.get_assistant(assistant_id)

# Update assistant
assistant = client.update_assistant(
    assistant_id,
    name="New Name",
    description="New description"
)

# Delete assistant
result = client.delete_assistant(assistant_id)
```

### Threads

```python
# Create thread
thread = client.create_thread(assistant_id)

# List threads
threads = client.list_threads(skip=0, limit=100)

# Get thread with messages
thread = client.get_thread(thread_id)

# Delete thread
result = client.delete_thread(thread_id)
```

### Messages

```python
# Send message
response = client.add_message(
    thread_id=thread_id,
    content="Your message here",
    files=["path/to/file.pdf"],  # Optional attachments
    llm_provider="openai",  # Optional
    model_name="gpt-4o",  # Optional
    stream=False  # Set to True for streaming
)

# Streaming messages
for chunk in client.add_message(thread_id, content="Hello", stream=True):
    if chunk.get('type') == 'content_streaming':
        print(chunk.get('content', ''), end='', flush=True)
```

### Tool Integration (Simplified in v1.0.3)

#### Tool Definitions
```python
# Use plain JSON objects (no verbose SDK classes needed!)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    }
]

assistant = client.create_assistant(
    name="Weather Assistant",
    tools=tools
)
```

#### Tool Call Handling
```python
# Enhanced object-oriented access with automatic JSON parsing
response = client.add_message(thread_id, content="What's the weather in NYC?")

if response.status == 'REQUIRES_ACTION' and response.tool_calls:
    for tc in response.tool_calls:
        function_name = tc.function.name           # Direct property access
        function_args = tc.function.parsed_arguments  # Auto JSON parsing
        tool_call_id = tc.id                       # Direct property access
        
        # Your tool logic here
        result = handle_tool_call(function_name, function_args)
        
        # Submit results using plain dictionaries
        client.submit_tool_outputs(
            thread_id=thread_id,
            run_id=response.run_id,
            tool_outputs=[{
                "tool_call_id": tool_call_id,
                "output": result
            }]
        )
```

### Documents

```python
# Upload document to assistant
document = client.upload_document_to_assistant(
    assistant_id=assistant_id,
    file_path="path/to/document.pdf"
)

# Upload document to thread
document = client.upload_document_to_thread(
    thread_id=thread_id,
    file_path="path/to/document.pdf"
)

# List assistant documents
documents = client.list_assistant_documents(assistant_id)

# List thread documents
documents = client.list_thread_documents(thread_id)

# Get document status
document = client.get_document_status(document_id)

# Delete document
result = client.delete_document(document_id)
```

## Error Handling

The SDK includes comprehensive error handling:

```python
from backboard import (
    BackboardAPIError,
    BackboardValidationError,
    BackboardNotFoundError,
    BackboardRateLimitError,
    BackboardServerError
)

try:
    assistant = client.get_assistant("invalid_id")
except BackboardNotFoundError:
    print("Assistant not found")
except BackboardValidationError as e:
    print(f"Validation error: {e}")
except BackboardAPIError as e:
    print(f"API error: {e}")
```

## Supported File Types

The SDK supports uploading the following file types:
- PDF files (.pdf)
- Microsoft Office files (.docx, .xlsx, .pptx, .doc, .xls, .ppt)
- Text files (.txt, .csv, .md, .markdown)
- Code files (.py, .js, .html, .css, .xml)
- JSON files (.json, .jsonl)

## Requirements

- Python 3.8+
- requests >= 2.28.0

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: https://docs.backboard.io
- Issues: https://github.com/backboard/backboard-python-sdk/issues
- Email: support@backboard.io
