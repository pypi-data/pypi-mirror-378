# Daytona Environment MCP Tool Template

## Description

Secure and elastic infrastructure for running AI-generated code using Daytona sandboxes. Provides lightning-fast environment creation (sub-90ms), isolated runtime for secure code execution, programmatic control via File, Git, LSP, and Execute APIs, OCI/Docker compatibility, and unlimited persistence options. Perfect for development, testing, prototyping, and educational workflows where isolated execution environments are needed.

## Instructions

**Tool Type**: Direct method calls AND intent-based calls
**Tool ID**: daytona_environment

### Methods Available:
- **create_sandbox**: Create a new Daytona sandbox environment for development or testing
- **execute_code**: Run Python, JavaScript, or other code securely in a sandbox
- **execute_shell**: Execute shell commands and CLI operations in a sandbox
- **file_operation**: Perform file operations (read, write, upload, download, list, delete)
- **git_operation**: Perform git operations (clone, pull, push, commit, status, checkout)
- **list_sandboxes**: List all available Daytona sandbox environments
- **delete_sandbox**: Remove/destroy a sandbox environment
- **get_sandbox_info**: Get detailed information about a specific sandbox

### How to Use:
**For Direct Calls**: Call specific methods with structured parameters. Use create_sandbox to spin up new environments, execute_code to run code safely, file_operation to manage files, git_operation for version control, and other methods for environment management.

**For Intent-Based**: Describe what you want to do with development environments in natural language (e.g., "create a Python development environment", "run this code in a sandbox", "clone my repository into a new environment", "list my current sandboxes"). The system will parse your intent and execute the appropriate Daytona operation with intelligent parameter extraction.

### Parameters (for direct calls):

**For create_sandbox**:
- language (optional, default="python") - Programming language/runtime (python, javascript, typescript, java, go, etc.)
- image (optional) - Docker image name (e.g., "python:3.9", "node:18")
- name (optional) - Human-readable name for the sandbox
- git_repo (optional) - Git repository URL to clone during creation
- git_branch (optional, default="main") - Git branch to checkout
- environment_vars (optional) - Environment variables as key-value pairs
- persistent (optional, default=false) - Whether sandbox persists after session

**For execute_code**:
- sandbox_id (required) - Target sandbox identifier
- code (required) - Code to execute
- language (optional) - Programming language, defaults from context
- working_directory (optional) - Directory to run code from

**For execute_shell**:
- sandbox_id (required) - Target sandbox identifier
- command (required) - Shell command to execute
- working_directory (optional) - Directory to run command from

**For file_operation**:
- sandbox_id (required) - Target sandbox identifier
- operation (required) - File operation type: "read", "write", "upload", "download", "list", "delete"
- file_path (required) - Target file or directory path in sandbox
- content (optional) - File content for write operations
- local_path (optional) - Local file path for upload/download operations

**For git_operation**:
- sandbox_id (required) - Target sandbox identifier
- operation (required) - Git operation: "clone", "pull", "push", "status", "commit", "checkout"
- repository_url (optional) - Git repository URL for clone operations
- branch (optional) - Branch name for checkout/clone operations
- commit_message (optional) - Commit message for commit operations
- working_directory (optional) - Directory to perform git operations in

**For delete_sandbox**:
- sandbox_id (required) - Sandbox identifier to delete

**For get_sandbox_info**:
- sandbox_id (required) - Sandbox identifier to get information about

**For list_sandboxes**:
- No parameters required

### Response Format:
All methods return structured responses with success/error status, relevant data, and descriptive messages. Successful operations include operation-specific data like sandbox IDs, execution output, file contents, or git operation results.

### Environment Variables Required:
- DAYTONA_API_KEY - Your Daytona API key (required)
- DAYTONA_API_URL - Daytona API URL (optional, defaults to app.daytona.io)

### Common Use Cases:

**Development Environment Setup**:
```
"Create a Python development environment and clone my Flask project"
"Set up a Node.js sandbox with TypeScript support"
"Create a persistent environment for machine learning work"
```

**Code Execution & Testing**:
```
"Run this Python script in a clean environment"
"Execute these unit tests in a sandbox"
"Test this code snippet safely"
```

**File Management**:
```
"Upload my project files to the sandbox"
"Read the contents of main.py in my environment"
"List all files in the /app directory"
```

**Git Operations**:
```
"Clone my repository into the sandbox"
"Commit and push the changes"
"Check the git status of my project"
```

**Environment Management**:
```
"Show me all my current sandboxes"
"Get details about sandbox-abc123"
"Delete the old testing environment"
```

### Security Features:
- Isolated execution environments prevent code from affecting host system
- Secure file operations with controlled access
- Environment variables and secrets management
- Automatic cleanup and resource management
- Permission-based access controls

### Performance Features:
- Sub-90ms sandbox creation time
- Concurrent execution support
- Automatic resource optimization
- Persistent storage options
- Preview URL generation for web applications

This tool is ideal for developers, educators, and teams who need secure, fast, and scalable code execution environments with full development toolchain support.


