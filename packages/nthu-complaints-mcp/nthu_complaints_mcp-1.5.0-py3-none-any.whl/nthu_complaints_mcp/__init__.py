"""
NTHU Complaints System FastMCP Server

A FastMCP server for managing NTHU complaint system operations including:
- User authentication
- Complaint submission
- Complaint management and tracking
"""

__version__ = "1.5.0"
__author__ = "NTHU Complaints System Team"

from .server import create_server, main

__all__ = ["create_server", "main"]