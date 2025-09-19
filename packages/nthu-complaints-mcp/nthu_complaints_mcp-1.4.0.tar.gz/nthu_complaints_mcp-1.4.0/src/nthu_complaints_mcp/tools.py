"""MCP tools for NTHU complaints system."""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .firebase_client import firebase_client
from .session_manager import session_manager

logger = logging.getLogger(__name__)


def login_user(email: str, password: str) -> Dict[str, Any]:
    """
    用戶登入功能

    Args:
        email: 用戶電子郵件
        password: 用戶密碼

    Returns:
        包含用戶資訊和會話令牌的字典
    """
    try:
        # Note: This is a simplified authentication for demo purposes
        # In a real implementation, you would verify password against a secure hash

        # Get user by email using REST client
        user = firebase_client.get_user_by_email(email)

        # Get user data from Firestore
        user_doc = firebase_client.db.collection('users').document(user['uid']).get()

        if not user_doc:
            return {
                "success": False,
                "error": "用戶資料不存在"
            }

        user_data = user_doc

        # Create session
        session_data = {
            "uid": user['uid'],
            "email": email,
            "role": user_data.get('role', 'user'),
            "department": user_data.get('department'),
            "permissions": user_data.get('permissions', []),
            "display_name": user_data.get('displayName', email)
        }

        session_token = session_manager.create_session(session_data)

        return {
            "success": True,
            "user": {
                "uid": user['uid'],
                "email": email,
                "role": user_data.get('role', 'user'),
                "department": user_data.get('department'),
                "display_name": user_data.get('displayName', email)
            },
            "session_token": session_token
        }

    except RuntimeError as e:
        if "not found" in str(e).lower():
            return {
                "success": False,
                "error": "用戶不存在"
            }
        else:
            raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        return {
            "success": False,
            "error": f"登入失敗: {str(e)}"
        }


def submit_complaint(
    session_token: str,
    title: str,
    description: str,
    category: str,
    department: str,
    priority: str = "medium",
    anonymous: bool = False,
    contact_info: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    提交新的申訴

    Args:
        session_token: 用戶會話令牌
        title: 申訴標題
        description: 申訴詳細描述
        category: 申訴類別
        department: 相關部門
        priority: 優先級 (low, medium, high)
        anonymous: 是否匿名申訴
        contact_info: 聯絡資訊 (如果非匿名)

    Returns:
        包含申訴編號和狀態的字典
    """
    # Verify session
    user_session = session_manager.get_session(session_token)
    if not user_session:
        return {
            "success": False,
            "error": "會話已過期，請重新登入"
        }

    try:
        # Generate case number
        timestamp = datetime.now()
        case_number = f"NTHU{timestamp.strftime('%Y%m%d')}{timestamp.strftime('%H%M%S')}"

        # Prepare complaint data
        complaint_data = {
            "caseNumber": case_number,
            "title": title,
            "description": description,
            "category": category,
            "department": department,
            "priority": priority,
            "status": "pending",
            "anonymous": anonymous,
            "submittedAt": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "submittedBy": user_session["uid"] if not anonymous else None,
            "submitterEmail": user_session["email"] if not anonymous else None,
            "contactInfo": contact_info if not anonymous else None,
            "responses": [],
            "statusHistory": [
                {
                    "status": "pending",
                    "timestamp": datetime.now().isoformat(),
                    "note": "申訴已提交"
                }
            ]
        }

        # Add to Firestore
        doc_ref = firebase_client.db.collection('complaints').add(complaint_data)

        return {
            "success": True,
            "case_number": case_number,
            "complaint_id": doc_ref['id'],
            "message": f"申訴已成功提交，案件編號: {case_number}"
        }

    except Exception as e:
        logger.error(f"Submit complaint error: {e}")
        return {
            "success": False,
            "error": f"提交申訴失敗: {str(e)}"
        }


def get_user_complaints_summary(session_token: str) -> Dict[str, Any]:
    """
    查看當前用戶的所有申訴摘要

    Args:
        session_token: 用戶會話令牌

    Returns:
        包含申訴列表的字典
    """
    # Verify session
    user_session = session_manager.get_session(session_token)
    if not user_session:
        return {
            "success": False,
            "error": "會話已過期，請重新登入"
        }

    try:
        # Query user's complaints
        complaints_ref = firebase_client.db.collection('complaints')

        if user_session["role"] == "admin":
            # Admin can see all complaints (simplified implementation)
            query = complaints_ref
        else:
            # Regular users can only see their own complaints
            query = complaints_ref.where('submittedBy', '==', user_session["uid"])

        complaints = list(query.stream())

        complaint_list = []
        for data in complaints:
            complaint_list.append({
                "case_number": data.get("caseNumber"),
                "title": data.get("title"),
                "category": data.get("category"),
                "department": data.get("department"),
                "status": data.get("status"),
                "priority": data.get("priority"),
                "submitted_at": data.get("submittedAt"),
                "last_updated": data.get("lastUpdated"),
                "anonymous": data.get("anonymous", False)
            })

        return {
            "success": True,
            "complaints": complaint_list,
            "total_count": len(complaint_list)
        }

    except Exception as e:
        logger.error(f"Get complaints summary error: {e}")
        return {
            "success": False,
            "error": f"查詢申訴列表失敗: {str(e)}"
        }


def get_complaint_details(session_token: str, case_number: str) -> Dict[str, Any]:
    """
    查看特定申訴的詳細資訊

    Args:
        session_token: 用戶會話令牌
        case_number: 申訴案件編號

    Returns:
        包含申訴詳細資訊的字典
    """
    # Verify session
    user_session = session_manager.get_session(session_token)
    if not user_session:
        return {
            "success": False,
            "error": "會話已過期，請重新登入"
        }

    try:
        # Query complaint by case number
        complaints_ref = firebase_client.db.collection('complaints')
        query = complaints_ref.where('caseNumber', '==', case_number)
        complaints = list(query.stream())

        if not complaints:
            return {
                "success": False,
                "error": "找不到指定的申訴案件"
            }

        complaint_data = complaints[0]

        # Check permissions
        if (user_session["role"] != "admin" and
            complaint_data.get("submittedBy") != user_session["uid"]):
            return {
                "success": False,
                "error": "無權限查看此申訴案件"
            }

        # Format response data
        responses = []
        for response in complaint_data.get("responses", []):
            responses.append({
                "type": response.get("type"),
                "content": response.get("content"),
                "author": response.get("author"),
                "timestamp": response.get("timestamp")
            })

        status_history = []
        for status in complaint_data.get("statusHistory", []):
            status_history.append({
                "status": status.get("status"),
                "note": status.get("note"),
                "timestamp": status.get("timestamp")
            })

        complaint_details = {
            "case_number": complaint_data.get("caseNumber"),
            "title": complaint_data.get("title"),
            "description": complaint_data.get("description"),
            "category": complaint_data.get("category"),
            "department": complaint_data.get("department"),
            "status": complaint_data.get("status"),
            "priority": complaint_data.get("priority"),
            "anonymous": complaint_data.get("anonymous", False),
            "submitted_at": complaint_data.get("submittedAt"),
            "last_updated": complaint_data.get("lastUpdated"),
            "contact_info": complaint_data.get("contactInfo") if not complaint_data.get("anonymous") else None,
            "responses": responses,
            "status_history": status_history
        }

        return {
            "success": True,
            "complaint": complaint_details
        }

    except Exception as e:
        logger.error(f"Get complaint details error: {e}")
        return {
            "success": False,
            "error": f"查詢申訴詳情失敗: {str(e)}"
        }


def logout_user(session_token: str) -> Dict[str, Any]:
    """
    用戶登出功能

    Args:
        session_token: 用戶會話令牌

    Returns:
        登出狀態
    """
    if session_manager.delete_session(session_token):
        return {
            "success": True,
            "message": "已成功登出"
        }
    else:
        return {
            "success": False,
            "error": "會話不存在或已過期"
        }


def check_session_status(session_token: str) -> Dict[str, Any]:
    """
    檢查會話狀態

    Args:
        session_token: 用戶會話令牌

    Returns:
        會話狀態和用戶資訊
    """
    user_session = session_manager.get_session(session_token)
    if user_session:
        return {
            "success": True,
            "valid": True,
            "user": {
                "email": user_session["email"],
                "role": user_session["role"],
                "department": user_session["department"],
                "display_name": user_session["display_name"],
                "login_time": user_session["created_at"]
            }
        }
    else:
        return {
            "success": True,
            "valid": False,
            "message": "會話不存在或已過期"
        }