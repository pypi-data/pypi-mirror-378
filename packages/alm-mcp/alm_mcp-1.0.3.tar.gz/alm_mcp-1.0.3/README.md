# Polarion ALM MCP Server

A Model Context Protocol (MCP) server for Polarion ALM (Application Lifecycle Management) integration. This server provides tools for managing projects, work items, attachments, comments, and other ALM operations through the Polarion REST API.

## Features

- **Project Management**: List and retrieve project information
- **Work Item Operations**: Create, read, update, delete, and query work items
- **Assignee Management**: Add and retrieve work item assignees
- **Attachment Handling**: Upload, list, and remove attachments
- **Comment System**: Add, list, and remove comments
- **Link Role Management**: Manage work item relationships
- **Watcher Management**: Add and remove watchers for work items

## Installation

### Option 1: Local Development Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd alm-mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional):
```bash
cp .env.example .env
# Edit .env with your Polarion credentials
```

### Option 2: Package Installation (Future)

```bash
# For future package distribution
uvx alm-mcp
# or
pip install alm-mcp
```

## Configuration

The MCP server supports multiple configuration methods with the following priority:

1. **Command line arguments** (highest priority)
2. **Environment variables** (lower priority)

### Authentication Methods

The server supports three authentication methods:

1. **Access Token** (recommended):
   - `POLARION_ACCESS_TOKEN` or `--access-token`

2. **Username + Password**:
   - `POLARION_USERNAME` + `POLARION_PASSWORD` or `--username` + `--password`

3. **API Key only** (limited functionality):
   - `POLARION_API_KEY` or `--api-key`

### Environment Variables

Create a `.env` file with the following variables:

```env
POLARION_BASE_URL=your-alm-base-url
POLARION_API_KEY=your-api-key-here
POLARION_USERNAME=your-username
POLARION_PASSWORD=your-password
POLARION_ACCESS_TOKEN=your-access-token
```

## Usage

### Running the Server Directly

```bash
# Using environment variables
python main.py

# Using command line arguments
python main.py --base-url "your-alm-base-url" --access-token "your-token"

# Mixed approach (args override env vars)
python main.py --password "your-password"
```

### VS Code Integration with GitHub Copilot

#### Setup Steps

1. **Install GitHub Copilot Extension** in VS Code

2. **Create MCP Configuration**: Add the following to your project's `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "alm-mcp-server": {
      "command": "python",
      "args": ["/absolute/path/to/alm-mcp/main.py"],
      "env": {
        "POLARION_BASE_URL": "your-alm-base-url",
        "POLARION_ACCESS_TOKEN": "${input:alm_access_token}"
      },
      "type": "stdio"
    }
  },
  "inputs": [
    {
      "type": "promptString",
      "id": "alm_access_token",
      "description": "ALM Access Token",
      "password": true
    }
  ]
}
```

3. **Update File Paths**: Replace `/absolute/path/to/alm-mcp/main.py` with the actual path to your `main.py` file

4. **Restart VS Code** to load the MCP server configuration

#### Alternative Configuration Methods

The `mcp-config-examples/` directory contains several configuration templates:

- **`direct-python.json`**: Direct Python execution with environment variables
- **`command-line-args.json`**: Using command line arguments instead of env vars
- **`uvx-package.json`**: For future package installation via uvx

#### Configuration Priority

When both environment variables and command line arguments are provided:
- Command line arguments take precedence
- Environment variables are used as fallback
- VS Code will prompt for sensitive values using the `inputs` configuration

#### Security Notes

- Use `${input:variable_name}` for sensitive values to prompt user input
- Set `"password": true` in inputs for password fields
- Never commit actual credentials to version control

### Available Tools

#### Project Operations
- `get_projects` - Get all projects
- `get_project` - Get specific project information

#### Work Item Operations
- `get_work_item` - Get specific work item
- `create_work_item` - Create new work item
- `update_work_item` - Update existing work item
- `delete_work_item` - Delete work item
- `query_work_items` - Query work items using Lucene syntax

#### Assignee Operations
- `get_assignees` - Get work item assignees
- `add_assignee` - Add assignee to work item

#### Attachment Operations
- `get_attachments` - Get work item attachments
- `add_attachment` - Add attachment to work item
- `remove_attachment` - Remove attachment from work item

#### Comment Operations
- `get_comments` - Get work item comments
- `add_comment` - Add comment to work item
- `remove_comment` - Remove comment from work item

### Example Tool Usage

#### Query Work Items
```json
{
  "name": "query_work_items",
  "arguments": {
    "project_id": "PROJECT_ID",
    "query": "type:task AND status:open"
  }
}
```

#### Create Work Item
```json
{
  "name": "create_work_item",
  "arguments": {
    "project_id": "PROJECT_ID",
    "work_item_data": {
      "title": "New Task",
      "type": "task",
      "description": "Task description"
    }
  }
}
```

#### Add Comment
```json
{
  "name": "add_comment",
  "arguments": {
    "project_id": "PROJECT_ID",
    "work_item_id": "WORK_ITEM_ID",
    "comment_data": {
      "text": "This is a comment"
    }
  }
}
```

## API Endpoints Supported

Based on the Polarion REST API specification:

- `/projects` - Project listing and details
- `/workitems/{projectId}` - Work item operations
- `/workitems/{projectId}/query` - Work item queries
- `/workitems/{projectId}/{workItemId}/assignees` - Assignee management
- `/workitems/{projectId}/{workItemId}/attachments` - Attachment management
- `/workitems/{projectId}/{workItemId}/link-roles` - Link role management
- `/workitems/{projectId}/{workItemId}/watchers` - Watcher management
- `/workitems/{projectId}/{workItemId}/comments` - Comment management

## Authentication

The server uses the following authentication methods as required by Polarion:

- **API Key**: Sent via `x-apikey` header
- **Basic Authentication**: Username/password combination

## Error Handling

The server includes comprehensive error handling:

- HTTP status code validation
- Connection timeout handling
- JSON parsing error handling
- Missing environment variable validation
- Detailed error logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[MIT License. Copyright (c) 2025 hy74.hwang@gmail.com]