# AMPA SDK

The AMPA SDK is a Python library that provides a convenient, high-level interface for interacting with the AMPA API. It is designed to simplify prompt management, versioning, and execution from any Python application, script, or notebook.

## Overview

- **Easy integration**: Manage prompts and their versions with simple Python calls
- **Handles authentication**: Securely connect to the AMPA API with username/password or environment variables
- **Request/response abstraction**: No need to manually format HTTP requests
- **Extensible**: Add custom methods or extend for new API endpoints

## Features

- Create, update, delete, and run prompts from Python
- List and manage prompt versions
- Automatic handling of API authentication and errors
- Works with both local and remote AMPA API deployments
- CRUD and search for the `prompt_tests` endpoints

## Installation

To install the AMPA SDK, use pip:

```bash
pip install the37lab_ampa_sdk
```

## Configuration

You can configure the SDK via parameters or environment variables:

- `ampa_url`: The base URL of the AMPA API (default: https://ampa.the37lab.com:13002/)
- `username`: API username
- `password`: API password

Environment variables:
- `AMPA_API_URL`
- `AMPA_API_USERNAME`
- `AMPA_API_PASSWORD`

## Usage Example

```python
from the37lab_ampa_sdk import PromptAPI

# Initialize the client (parameters or env vars)
client = PromptAPI(
    ampa_url="http://localhost:8000",
    username="your_username",
    password="your_password",
)

# Create an prompt
data = {
    "prompt_name": "My Prompt",
    "description": "A helpful assistant",
    "purpose": "You are a helpful assistant",
    "instruction": "Tell a story about Sweden"
}
prompt = client.create_prompt(data)

# Run the prompt
response = client.call_prompt(
    "My Prompt",
    variables={"name": "John"},
    prompt="Tell me a story"
)

# List prompt versions
versions = client.list_prompt_versions(prompt["id"])
```

## Use Cases

- Integrate prompt management into Python apps, scripts, or notebooks
- Automate prompt creation and execution in pipelines
- Rapid prototyping and experimentation with LLM prompts

## Extensibility

- Add new methods for custom API endpoints
- Subclass `PromptAPI` to add custom logic or error handling

## Troubleshooting

- Ensure the AMPA API is running and accessible
- Check credentials and API URL
- Review exception messages for error details

## License

This project is proprietary software. All rights reserved.

## prompt_tests Table Usage

The SDK supports CRUD and search for the `prompt_tests` endpoints:

```python
from the37lab_ampa_sdk import PromptAPI
client = PromptAPI(...)

# Create
data = {
    'name': 'Test',
    'description': 'desc',
    'data': {'foo': 'bar'},
    'prompt': 'Say hi',
    'prompt_ids': [1, 2]
}
r = client.create_prompt_test(**data)

# Get by id
r = client.get_prompt_test(r['id'])

# Update
r = client.update_prompt_test(r['id'], description='new desc')

# Delete
client.delete_prompt_test(r['id'])

# List all
rows = client.list_prompt_tests()

# List by prompt id
rows = client.list_prompt_tests_by_prompt_id(1)
```

