"""
NTHU Complaints MCP Server Data Models

Pydantic models for request/response validation and data structure.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, field_validator


class ComplaintType(str, Enum):
    """Valid complaint types."""
    ACADEMIC_RULES = "academic_rules"
    ADMINISTRATIVE = "administrative"
    FACILITIES = "facilities"
    OTHER = "other"


class ComplaintStatus(str, Enum):
    """Valid complaint status values."""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class ComplaintSubmission(BaseModel):
    """Model for complaint submission data."""
    email: EmailStr
    name: str
    complaint_type: ComplaintType
    complaint_details: str
    expected_action: str
    phone: Optional[str] = None
    student_id: Optional[str] = None
    department: Optional[str] = None

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @field_validator('complaint_details')
    @classmethod
    def details_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Complaint details cannot be empty')
        return v.strip()

    @field_validator('expected_action')
    @classmethod
    def action_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Expected action cannot be empty')
        return v.strip()


class ComplaintTracker(BaseModel):
    """Model for complaint tracking data."""
    case_number: str
    verification_code: str
    user_id: Optional[str] = None

    @field_validator('case_number')
    @classmethod
    def case_number_format(cls, v):
        if not v or len(v) < 5:
            raise ValueError('Invalid case number format')
        return v.upper()


class ComplaintDetails(BaseModel):
    """Model for complaint details response."""
    case_number: str
    verification_code: str

    @field_validator('case_number')
    @classmethod
    def case_number_format(cls, v):
        if not v or len(v) < 5:
            raise ValueError('Invalid case number format')
        return v.upper()


class ComplaintResponse(BaseModel):
    """Model for API response data."""
    success: bool
    message: str
    case_number: Optional[str] = None
    verification_code: Optional[str] = None
    status: Optional[ComplaintStatus] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    details: Optional[Dict[str, Any]] = None
    tracking_history: Optional[List[Dict[str, Any]]] = None


class APITestResult(BaseModel):
    """Model for API test results."""
    success: bool
    status_code: Optional[int] = None
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: datetime = datetime.now()


class FullTestResult(BaseModel):
    """Model for full test suite results."""
    test_summary: str
    overall_success: bool
    tests: List[Dict[str, Any]]
    message: str
    error: Optional[str] = None
    total_execution_time: Optional[float] = None
    timestamp: datetime = datetime.now()