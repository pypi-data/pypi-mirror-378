# aicodetools

Simple, lightweight AI code tools with Docker-only support. No complex dependencies.

Provides four essential tools for AI agents: **read**, **write**, **edit**, and **run** commands.
Runs in a secure Docker container with automatic setup and management.


## Installation

You can install the package using pip:

```bash
pip install aicodetools
```

Or for development:

```bash
pip install -e .
```

## Quick Start

```python
from aicodetools import CodeToolsClient

# Auto-starts Docker server if needed (uses default image)
client = CodeToolsClient(auto_start=True)

# Or use a custom Docker image
# client = CodeToolsClient(auto_start=True, docker_image="python:3.11-slim")

# Read a file with smart token management
result = client.read_file("example.py")
print(result["content"])

# Write a file (with safety checks)
client.write_file("hello.py", "print('Hello, World!')")

# Edit file using string replacement
client.edit_file("hello.py", "Hello", "Hi")

# Run commands (non-interactive)
result = client.run_command("python hello.py", interactive=False)
print(result["stdout"])

# Run interactive commands with simplified API
client.run_command("python -i", interactive=True)
client.send_input("2 + 2")
output = client.get_output()

# Clean up when done
client.stop_server()
```

## Docker Configuration

### Using Custom Docker Images

You can specify your own Docker image instead of the default `aicodetools:latest`:

```python
from aicodetools import CodeToolsClient

# Use a custom Python image
client = CodeToolsClient(
    auto_start=True,
    docker_image="python:3.11-slim"
)

# Use custom port (default is 18080 to avoid conflicts)
client = CodeToolsClient(
    auto_start=True,
    port=19080  # Use different port if needed
)

# Use your own custom image with dependencies pre-installed
client = CodeToolsClient(
    auto_start=True,
    docker_image="my-company/python-tools:latest"
)

# Use a specific tag
client = CodeToolsClient(
    auto_start=True,
    docker_image="python:3.12-alpine"
)
```

### Docker Image Requirements

Your custom Docker image must have:
- Python 3.10+ installed
- Required packages: `requests`, `tiktoken`, `pydantic`
- Access to install packages (for the aicodetools server)

### Example Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install requests tiktoken pydantic

# Set working directory
WORKDIR /workspace

# Optional: Pre-install common packages
RUN pip install numpy pandas requests beautifulsoup4

CMD ["/bin/bash"]
```

### Manual Docker Usage

If you prefer to manage Docker yourself:

```bash
# Build and run your own container
docker build -t my-codetools .
docker run -d -p 18080:8080 -v $(pwd):/workspace my-codetools \
  python -m aicodetools.server

# Then connect without auto_start (using custom port)
client = CodeToolsClient(auto_start=False, server_url="http://localhost:18080")

# Or use a different port entirely
docker run -d -p 19080:8080 -v $(pwd):/workspace my-codetools \
  python -m aicodetools.server
client = CodeToolsClient(auto_start=False, server_url="http://localhost:19080")
```

## Core Tools

Four essential tools, designed for simplicity and reliability:

### 📖 **Read Tool**
- Smart file reading with tiered token management (4k/10k modes)
- Regex pattern matching with context lines
- Line range support for targeted reading
- Automatic compression for long lines (6k max per line)

### ✏️ **Write Tool**
- Safe file writing with read-first validation for existing files
- Automatic backup creation with timestamps
- UTF-8 encoding by default (simplified for Linux containers)
- Directory creation if needed

### ✂️ **Edit Tool**
- String-based find and replace editing
- Support for single or all occurrences (replace_all flag)
- Automatic backup before editing
- Detailed change reporting with diffs

### ⚡ **Run Tool**
- **Single function**: `run_command(command, timeout=300, interactive=False)`
- **Non-interactive**: Auto-kill on timeout, return complete results
- **Interactive**: Stream output, agent controls (get_output, send_input, stop_process)
- **Single command limit**: Only one command at a time (prevents agent confusion)

## Usage Examples

### Context Manager Usage

```python
from aicodetools import CodeToolsClient

# Recommended: Use context manager for automatic cleanup
with CodeToolsClient(auto_start=True) as client:
    # Read file with regex pattern matching
    matches = client.read_file("example.py", regex=r"def \w+")

    # Safe file editing workflow
    client.read_file("config.py")  # Read first for safety
    client.edit_file("config.py", "DEBUG = False", "DEBUG = True")

    # Execute multiple commands (non-interactive)
    client.run_command("pip install requests", interactive=False)
    result = client.run_command("python -c 'import requests; print(requests.__version__)'", interactive=False)
    print(f"Requests version: {result['stdout']}")

# Server automatically stops when exiting context
```

### Interactive Command Example

```python
from aicodetools import CodeToolsClient
import time

client = CodeToolsClient(auto_start=True)

# Start a Python REPL (interactive mode)
result = client.run_command("python -i", interactive=True)
print(f"Python REPL started: {result['success']}")

# Send commands and get output
client.send_input("x = 10")
client.send_input("y = 20")
client.send_input("print(x + y)")

# Get accumulated output
time.sleep(1)  # Wait for commands to execute
output = client.get_output()
print("Python REPL output:", output["recent_stdout"])

# Stop the process
client.stop_process()
client.stop_server()
```

### AI Agent Integration

```python
from aicodetools import CodeToolsClient

def create_tool_functions():
    """Create tool functions for AI agent integration."""
    client = CodeToolsClient(auto_start=True)

    def read_file_tool(file_path: str, max_lines: int = None):
        """Read file content."""
        return client.read_file(file_path, max_lines=max_lines)

    def write_file_tool(file_path: str, content: str):
        """Write content to file."""
        return client.write_file(file_path, content)

    def edit_file_tool(file_path: str, old_text: str, new_text: str):
        """Edit file by replacing text."""
        # Safe workflow: read first, then edit
        client.read_file(file_path)
        return client.edit_file(file_path, old_text, new_text)

    def run_command_tool(command: str, timeout: int = 300, interactive: bool = False):
        """Run shell command."""
        return client.run_command(command, timeout=timeout, interactive=interactive)

    return [read_file_tool, write_file_tool, edit_file_tool, run_command_tool], client

# Use with your favorite AI framework
tools, client = create_tool_functions()

# Your AI agent can now use these tools
# agent = YourAIAgent(tools=tools)
# response = agent.run("Create a Python script that calculates fibonacci numbers")

# Clean up when done
client.stop_server()
```

## Architecture

### 🐳 **Docker-Only Design**
- Simplified deployment: Only Docker containers supported
- Auto-fallback: Creates base container if Docker not running
- Secure isolation: All operations run in containerized environment
- No complex environment management

### 🏗️ **Server-Client Model**
- **Server**: Runs in Docker container, handles tool execution
- **Client**: Python interface, communicates via HTTP/JSON API
- **Auto-start**: Client automatically manages Docker server lifecycle
- **Stateless**: Clean separation between client and execution environment

### 🎯 **Key Benefits**
- **Simplicity**: 4 core tools vs 14+ complex tools in v1
- **Reliability**: Docker-only, predictable environment
- **Maintainability**: Simple codebase, clear architecture
- **Performance**: Lightweight, fast startup
- **Agent-Friendly**: Better error messages, token awareness

## Requirements

- Python 3.10+
- Docker (required - no local fallback)
- Minimal dependencies: `requests`, `tiktoken`

## Development

### Code Quality 🧹

- `make style` to format the code
- `make check_code_quality` to check code quality (PEP8 basically)
- `black .`
- `ruff . --fix`

### Tests 🧪

[`pytests`](https://docs.pytest.org/en/7.1.x/) is used to run our tests.

### Publishing 🚀

```bash
poetry build
poetry publish
```

## License

MIT
