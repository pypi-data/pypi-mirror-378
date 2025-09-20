#!/usr/bin/env python3
"""
Copyright (c) 2025 hy74.hwang@gmail.com
SPDX-License-Identifier: MIT
Licensed under the MIT License.

Polarion ALM MCP Server

A Model Context Protocol server for Polarion ALM (Application Lifecycle Management) integration.
Provides tools for managing projects, work items, attachments, and other ALM operations.
"""

import argparse
import asyncio
import json
import logging
import os
import base64
import sys
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolarionClient:
    """Polarion ALM REST API Client"""

    def __init__(self, base_url: str, access_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')

        # Setup headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Setup authentication - Only personal access tokens are allowed for security
        if access_token:
            # Only Bearer token format is supported for personal access tokens
            if access_token.startswith('Bearer '):
                headers["Authorization"] = access_token
            else:
                headers["Authorization"] = f"Bearer {access_token}"
            logger.debug("Personal access token authentication configured")
        else:
            logger.warning("No personal access token provided. Authentication is required for ALM operations.")

        # Log configured headers (without sensitive data)
        safe_headers = {k: v if k not in ["Authorization"] else "[REDACTED]"
                      for k, v in headers.items()}
        logger.debug(f"Request headers configured: {safe_headers}")

        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers=headers
        )

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Polarion API"""
        # Properly construct URL by ensuring base_url ends with / and endpoint starts without /
        base = self.base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')
        url = f"{base}/{endpoint}"

        logger.debug(f"Making {method} request to: {url}")

        try:
            response = await self.client.request(method, url, **kwargs)
            await response.aread()  # Ensure response is fully read
            response.raise_for_status()

            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"content": response.text, "status_code": response.status_code}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error(f"Authentication failed (401): Please check your credentials")
                logger.error(f"Response: {e.response.text[:200]}...")  # Limit response length
                raise Exception("Authentication failed: Please verify your API key, access token, or username/password")
            elif e.response.status_code == 403:
                logger.error(f"Access forbidden (403): Insufficient permissions")
                raise Exception("Access forbidden: Your credentials don't have sufficient permissions for this operation")
            elif e.response.status_code == 404:
                logger.error(f"Resource not found (404): {url}")
                raise Exception(f"Resource not found: {url}")
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text[:200]}...")
                raise Exception(f"API request failed: {e.response.status_code} - {e.response.text[:100]}...")
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {str(e)} - Check URL: {url}")
            raise Exception(f"Connection failed: {str(e)} - Please verify the base URL")
        except Exception as e:
            logger.error(f"Request error: {str(e)} - URL: {url}")
            raise Exception(f"Request failed: {str(e)}")

    # Project operations
    async def get_projects(self) -> Dict[str, Any]:
        """Get all projects"""
        return await self._request("GET", "/projects")

    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get specific project"""
        return await self._request("GET", f"/projects/{project_id}")

    # Work Item operations
    async def get_work_items_all(self, project_id: str) -> Dict[str, Any]:
        """Get all work items in a project"""
        return await self._request("GET", f"/projects/{project_id}/workitems")

    async def get_work_item(self, project_id: str, work_item_id: str) -> Dict[str, Any]:
        """Get specific work item"""
        return await self._request("GET", f"/projects/{project_id}/workitems/{work_item_id}")

    async def create_work_item(self, project_id: str, work_item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new work item"""
        return await self._request("POST", f"/projects/{project_id}/workitems", json=work_item_data)

    async def update_work_item(self, project_id: str, work_item_id: str, work_item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update work item"""
        return await self._request("PATCH", f"/projects/{project_id}/workitems/{work_item_id}", json=work_item_data)

    async def delete_work_item(self, project_id: str, work_item_id: str) -> Dict[str, Any]:
        """Delete work item"""
        return await self._request("DELETE", f"/projects/{project_id}/workitems/{work_item_id}")

    async def query_work_items(self, project_id: str, query: str) -> Dict[str, Any]:
        """Query work items using query parameter"""
        return await self._request("GET", f"/projects/{project_id}/workitems", params={"query": query})

    # Assignee operations
    async def get_assignees(self, project_id: str, work_item_id: str) -> Dict[str, Any]:
        """Get work item assignees"""
        return await self._request("GET", f"/projects/{project_id}/workitems/{work_item_id}/assignees")

    async def add_assignee(self, project_id: str, work_item_id: str, assignee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add assignee to work item"""
        return await self._request("POST", f"/projects/{project_id}/workitems/{work_item_id}/assignees", json=assignee_data)

    # Attachment operations
    async def get_attachments(self, project_id: str, work_item_id: str) -> Dict[str, Any]:
        """Get work item attachments"""
        return await self._request("GET", f"/projects/{project_id}/workitems/{work_item_id}/attachments")

    async def add_attachment(self, project_id: str, work_item_id: str, attachment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add attachment to work item"""
        return await self._request("POST", f"/projects/{project_id}/workitems/{work_item_id}/attachments", json=attachment_data)

    async def remove_attachment(self, project_id: str, work_item_id: str, attachment_id: str) -> Dict[str, Any]:
        """Remove attachment from work item"""
        return await self._request("DELETE", f"/projects/{project_id}/workitems/{work_item_id}/attachments/{attachment_id}")

    async def download_attachment(self, project_id: str, work_item_id: str, attachment_id: str) -> Dict[str, Any]:
        """Download attachment content"""
        return await self._request("GET", f"/projects/{project_id}/workitems/{work_item_id}/attachments/{attachment_id}/content")

    # Link Role operations
    async def get_link_roles(self, project_id: str, work_item_id: str) -> Dict[str, Any]:
        """Get work item link roles"""
        return await self._request("GET", f"/projects/{project_id}/workitems/{work_item_id}/link-roles/")

    async def add_link_role(self, project_id: str, work_item_id: str, link_role_id: str, link_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add link role to work item"""
        return await self._request("POST", f"/projects/{project_id}/workitems/{work_item_id}/link-roles/{link_role_id}", json=link_data)

    async def remove_link_role(self, project_id: str, work_item_id: str, link_role_id: str) -> Dict[str, Any]:
        """Remove link role from work item"""
        return await self._request("DELETE", f"/projects/{project_id}/workitems/{work_item_id}/link-roles/{link_role_id}")

    # Watcher operations
    async def get_watchers(self, project_id: str, work_item_id: str) -> Dict[str, Any]:
        """Get work item watchers"""
        return await self._request("GET", f"/projects/{project_id}/workitems/{work_item_id}/watchers")

    async def add_watcher(self, project_id: str, work_item_id: str, watcher_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add watcher to work item"""
        return await self._request("POST", f"/projects/{project_id}/workitems/{work_item_id}/watchers", json=watcher_data)

    async def remove_watcher(self, project_id: str, work_item_id: str, user_id: str) -> Dict[str, Any]:
        """Remove watcher from work item"""
        return await self._request("DELETE", f"/projects/{project_id}/workitems/{work_item_id}/watchers/{user_id}")

    # Comment operations
    async def get_comments(self, project_id: str, work_item_id: str) -> Dict[str, Any]:
        """Get work item comments"""
        return await self._request("GET", f"/projects/{project_id}/workitems/{work_item_id}/comments")

    async def get_comment(self, project_id: str, work_item_id: str, comment_id: str) -> Dict[str, Any]:
        """Get specific work item comment"""
        return await self._request("GET", f"/projects/{project_id}/workitems/{work_item_id}/comments/{comment_id}")

    async def update_comment(self, project_id: str, work_item_id: str, comment_id: str, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update specific work item comment"""
        return await self._request("PATCH", f"/projects/{project_id}/workitems/{work_item_id}/comments/{comment_id}", json=comment_data)

    async def add_comment(self, project_id: str, work_item_id: str, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add comment to work item"""
        return await self._request("POST", f"/projects/{project_id}/workitems/{work_item_id}/comments", json=comment_data)

    async def remove_comment(self, project_id: str, work_item_id: str, comment_id: str) -> Dict[str, Any]:
        """Remove comment from work item"""
        return await self._request("DELETE", f"/projects/{project_id}/workitems/{work_item_id}/comments/{comment_id}")


# Global client instance
polarion_client: Optional[PolarionClient] = None

# Global configuration from environment variables or command line arguments
config = {}

def parse_arguments():
    """Parse command line arguments for MCP integration"""
    parser = argparse.ArgumentParser(description="Polarion ALM MCP Server")
    parser.add_argument("--base-url", help="Polarion base URL")
    parser.add_argument("--access-token", help="Polarion access token")

    return parser.parse_args()

def get_config_value(key: str, args: argparse.Namespace) -> Optional[str]:
    """Get configuration value from environment variables or command line arguments"""
    # Priority: command line args > environment variables
    # Convert environment variable key to argument attribute name
    # POLARION_BASE_URL -> base_url
    # POLARION_API_KEY -> api_key
    # POLARION_ACCESS_TOKEN -> access_token
    arg_attr = key.lower().replace("polarion_", "").replace("-", "_")

    if hasattr(args, arg_attr):
        arg_value = getattr(args, arg_attr)
        if arg_value:
            return arg_value

    return os.getenv(key)

def get_client() -> PolarionClient:
    """Get the Polarion client instance"""
    global polarion_client, config

    if polarion_client is None:
        # Get configuration from args or environment
        args = config.get('args', argparse.Namespace())

        base_url = get_config_value("POLARION_BASE_URL", args)
        access_token = get_config_value("POLARION_ACCESS_TOKEN", args)

        # Validate configuration - personal access token is required for security
        if not access_token:
            raise ValueError(
                "Missing authentication configuration. For security reasons, only personal access tokens are allowed.\n"
                "Please provide POLARION_ACCESS_TOKEN environment variable or --access-token argument."
            )

        polarion_client = PolarionClient(
            base_url=base_url,
            access_token=access_token
        )

    return polarion_client


# MCP Server setup
server = Server("polarion-alm")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_projects",
            description="Get all projects from Polarion ALM",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="get_project",
            description="Get specific project information",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID to retrieve"
                    }
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="get_work_item",
            description="Get specific work item information",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item ID"
                    }
                },
                "required": ["project_id", "work_item_id"]
            }
        ),
        Tool(
            name="create_work_item",
            description="Create a new work item",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_data": {
                        "type": "object",
                        "description": "Work item data (title, type, description, etc.)"
                    }
                },
                "required": ["project_id", "work_item_data"]
            }
        ),
        Tool(
            name="update_work_item",
            description="Update an existing work item",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item ID"
                    },
                    "work_item_data": {
                        "type": "object",
                        "description": "Updated work item data"
                    }
                },
                "required": ["project_id", "work_item_id", "work_item_data"]
            }
        ),
        Tool(
            name="delete_work_item",
            description="Delete a work item",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item ID"
                    }
                },
                "required": ["project_id", "work_item_id"]
            }
        ),
        Tool(
            name="query_work_items",
            description="Query work items using query parameter",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "query": {
                        "type": "string",
                        "description": "Query string for filtering work items"
                    }
                },
                "required": ["project_id", "query"]
            }
        ),
        Tool(
            name="get_assignees",
            description="Get work item assignees",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item ID"
                    }
                },
                "required": ["project_id", "work_item_id"]
            }
        ),
        Tool(
            name="add_assignee",
            description="Add assignee to work item",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item ID"
                    },
                    "assignee_data": {
                        "type": "object",
                        "description": "Assignee data (user ID, etc.)"
                    }
                },
                "required": ["project_id", "work_item_id", "assignee_data"]
            }
        ),
        Tool(
            name="get_attachments",
            description="Get work item attachments",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item ID"
                    }
                },
                "required": ["project_id", "work_item_id"]
            }
        ),
        Tool(
            name="add_attachment",
            description="Add attachment to work item",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item ID"
                    },
                    "attachment_data": {
                        "type": "object",
                        "description": "Attachment data (file name, content, etc.)"
                    }
                },
                "required": ["project_id", "work_item_id", "attachment_data"]
            }
        ),
        Tool(
            name="remove_attachment",
            description="Remove attachment from work item",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item ID"
                    },
                    "attachment_id": {
                        "type": "string",
                        "description": "Attachment ID"
                    }
                },
                "required": ["project_id", "work_item_id", "attachment_id"]
            }
        ),
        Tool(
            name="get_comments",
            description="Get work item comments",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item ID"
                    }
                },
                "required": ["project_id", "work_item_id"]
            }
        ),
        Tool(
            name="add_comment",
            description="Add comment to work item",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item ID"
                    },
                    "comment_data": {
                        "type": "object",
                        "description": "Comment data (text, etc.)"
                    }
                },
                "required": ["project_id", "work_item_id", "comment_data"]
            }
        ),
        Tool(
            name="remove_comment",
            description="Remove comment from work item",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item ID"
                    },
                    "comment_id": {
                        "type": "string",
                        "description": "Comment ID"
                    }
                },
                "required": ["project_id", "work_item_id", "comment_id"]
            }
        ),
        Tool(
            name="get_all_work_items",
            description="Get all work items in a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    }
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="get_comment_details",
            description="Get specific work item comment details",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item ID"
                    },
                    "comment_id": {
                        "type": "string",
                        "description": "Comment ID"
                    }
                },
                "required": ["project_id", "work_item_id", "comment_id"]
            }
        ),
        Tool(
            name="update_comment",
            description="Update specific work item comment",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item ID"
                    },
                    "comment_id": {
                        "type": "string",
                        "description": "Comment ID"
                    },
                    "comment_data": {
                        "type": "object",
                        "description": "Updated comment data"
                    }
                },
                "required": ["project_id", "work_item_id", "comment_id", "comment_data"]
            }
        ),
        Tool(
            name="download_attachment",
            description="Download attachment content from work item",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "work_item_id": {
                        "type": "string",
                        "description": "Work item ID"
                    },
                    "attachment_id": {
                        "type": "string",
                        "description": "Attachment ID"
                    }
                },
                "required": ["project_id", "work_item_id", "attachment_id"]
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls"""
    try:
        client = get_client()

        if name == "get_projects":
            result = await client.get_projects()

        elif name == "get_project":
            result = await client.get_project(arguments["project_id"])

        elif name == "get_work_item":
            result = await client.get_work_item(arguments["project_id"], arguments["work_item_id"])

        elif name == "create_work_item":
            result = await client.create_work_item(arguments["project_id"], arguments["work_item_data"])

        elif name == "update_work_item":
            result = await client.update_work_item(
                arguments["project_id"],
                arguments["work_item_id"],
                arguments["work_item_data"]
            )

        elif name == "delete_work_item":
            result = await client.delete_work_item(arguments["project_id"], arguments["work_item_id"])

        elif name == "query_work_items":
            result = await client.query_work_items(arguments["project_id"], arguments["query"])

        elif name == "get_assignees":
            result = await client.get_assignees(arguments["project_id"], arguments["work_item_id"])

        elif name == "add_assignee":
            result = await client.add_assignee(
                arguments["project_id"],
                arguments["work_item_id"],
                arguments["assignee_data"]
            )

        elif name == "get_attachments":
            result = await client.get_attachments(arguments["project_id"], arguments["work_item_id"])

        elif name == "add_attachment":
            result = await client.add_attachment(
                arguments["project_id"],
                arguments["work_item_id"],
                arguments["attachment_data"]
            )

        elif name == "remove_attachment":
            result = await client.remove_attachment(
                arguments["project_id"],
                arguments["work_item_id"],
                arguments["attachment_id"]
            )

        elif name == "get_comments":
            result = await client.get_comments(arguments["project_id"], arguments["work_item_id"])

        elif name == "add_comment":
            result = await client.add_comment(
                arguments["project_id"],
                arguments["work_item_id"],
                arguments["comment_data"]
            )

        elif name == "remove_comment":
            result = await client.remove_comment(
                arguments["project_id"],
                arguments["work_item_id"],
                arguments["comment_id"]
            )

        elif name == "get_all_work_items":
            result = await client.get_work_items_all(arguments["project_id"])

        elif name == "get_comment_details":
            result = await client.get_comment(
                arguments["project_id"],
                arguments["work_item_id"],
                arguments["comment_id"]
            )

        elif name == "update_comment":
            result = await client.update_comment(
                arguments["project_id"],
                arguments["work_item_id"],
                arguments["comment_id"],
                arguments["comment_data"]
            )

        elif name == "download_attachment":
            result = await client.download_attachment(
                arguments["project_id"],
                arguments["work_item_id"],
                arguments["attachment_id"]
            )

        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

    except Exception as e:
        logger.error(f"Tool call error: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point"""
    global config

    # Parse command line arguments and store in global config
    args = parse_arguments()
    config['args'] = args

    # Log configuration (without sensitive data)
    logger.info("Starting Polarion ALM MCP Server")
    base_url = get_config_value("POLARION_BASE_URL", args)
    logger.info(f"Base URL: {base_url}")

    # Test client configuration
    try:
        client = get_client()
        logger.info("Client configuration validated successfully")

        # Log authentication method being used (without sensitive data)
        args = config.get('args', argparse.Namespace())
        if get_config_value("POLARION_ACCESS_TOKEN", args):
            logger.info("Using personal access token authentication (secure)")
        else:
            logger.warning("No authentication method configured")

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="polarion-alm",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())