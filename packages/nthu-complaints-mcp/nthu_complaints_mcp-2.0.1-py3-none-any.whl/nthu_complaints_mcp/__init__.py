"""
NTHU Complaints MCP Server

A Model Context Protocol (MCP) server for testing and interacting with
NTHU complaint system APIs. This package provides tools for submitting,
tracking, and managing student complaints through a standardized API interface.
"""

__version__ = "2.0.1"
__author__ = "NTHU Complaints Team"
__email__ = "complaints@nthu.edu.tw"
__description__ = "NTHU Complaints API Testing MCP Server"

from .server import NTHUComplaintsMCP
from .models import ComplaintSubmission, ComplaintTracker, ComplaintDetails
from .exceptions import NTHUComplaintsError, APIConnectionError, ValidationError

__all__ = [
    "NTHUComplaintsMCP",
    "ComplaintSubmission",
    "ComplaintTracker",
    "ComplaintDetails",
    "NTHUComplaintsError",
    "APIConnectionError",
    "ValidationError",
]