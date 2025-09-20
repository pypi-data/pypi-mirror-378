"""FastMCP server for NTHU Complaints System."""

import logging
import asyncio
from typing import Dict, Any, Optional
from fastmcp import FastMCP

from .firebase_client import firebase_client
from .session_manager import session_manager
from .tools import (
    login_user,
    submit_complaint,
    get_user_complaints_summary,
    get_complaint_details,
    logout_user,
    check_session_status,
    get_complaint_status
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """Create and configure the FastMCP server.

    Returns:
        Configured FastMCP server instance.
    """
    # Create FastMCP server
    mcp = FastMCP("NTHU Complaints System")

    @mcp.tool()
    def mcp_login_user(email: str, password: str) -> Dict[str, Any]:
        """
        用戶登入功能

        Args:
            email: 用戶電子郵件
            password: 用戶密碼

        Returns:
            包含用戶資訊和會話令牌的字典
        """
        return login_user(email, password)

    @mcp.tool()
    def mcp_submit_complaint(
        title: str,
        description: str,
        category: str,
        department: str,
        priority: str = "medium",
        anonymous: bool = True,
        contact_info: Optional[Dict] = None,
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        提交新的申訴 (支援匿名申訴，無需登入)

        Args:
            title: 申訴標題
            description: 申訴詳細描述
            category: 申訴類別
            department: 相關部門
            priority: 優先級 (low, medium, high)
            anonymous: 是否匿名申訴 (預設為True)
            contact_info: 聯絡資訊 (如果非匿名)
            session_token: 用戶會話令牌 (可選，如果提供則為登入用戶申訴)

        Returns:
            包含申訴編號和狀態的字典
        """
        return submit_complaint(
            title, description, category, department,
            priority, anonymous, contact_info, session_token
        )

    @mcp.tool()
    def mcp_get_user_complaints_summary(session_token: str) -> Dict[str, Any]:
        """
        查看當前用戶的所有申訴摘要

        Args:
            session_token: 用戶會話令牌

        Returns:
            包含申訴列表的字典
        """
        return get_user_complaints_summary(session_token)

    @mcp.tool()
    def mcp_get_complaint_details(session_token: str, case_number: str) -> Dict[str, Any]:
        """
        查看特定申訴的詳細資訊

        Args:
            session_token: 用戶會話令牌
            case_number: 申訴案件編號

        Returns:
            包含申訴詳細資訊的字典
        """
        return get_complaint_details(session_token, case_number)

    @mcp.tool()
    def mcp_logout_user(session_token: str) -> Dict[str, Any]:
        """
        用戶登出功能

        Args:
            session_token: 用戶會話令牌

        Returns:
            登出狀態
        """
        return logout_user(session_token)

    @mcp.tool()
    def mcp_check_session_status(session_token: str) -> Dict[str, Any]:
        """
        檢查會話狀態

        Args:
            session_token: 用戶會話令牌

        Returns:
            會話狀態和用戶資訊
        """
        return check_session_status(session_token)

    @mcp.tool()
    def mcp_get_complaint_status(case_number: str) -> Dict[str, Any]:
        """
        查詢申訴狀態 (無需登入，適用於匿名申訴)

        Args:
            case_number: 申訴案件編號

        Returns:
            申訴狀態和基本資訊
        """
        return get_complaint_status(case_number)

    @mcp.tool()
    def mcp_server_status() -> Dict[str, Any]:
        """
        獲取伺服器狀態

        Returns:
            伺服器狀態資訊
        """
        try:
            firebase_status = firebase_client._initialized
            active_sessions = session_manager.get_active_sessions_count()

            return {
                "success": True,
                "status": "running",
                "firebase_connected": firebase_status,
                "demo_mode": firebase_client._demo_mode,
                "active_sessions": active_sessions,
                "project_id": firebase_client._project_id if firebase_client._initialized else None
            }
        except Exception as e:
            logger.error(f"Server status error: {e}")
            return {
                "success": False,
                "error": f"獲取伺服器狀態失敗: {str(e)}"
            }

    return mcp


def main():
    """Main entry point for the MCP server."""
    logger.info("Starting NTHU Complaints MCP Server...")

    # Initialize Firebase
    if not firebase_client.initialize():
        logger.error("Failed to initialize Firebase. Please check your configuration.")
        return

    # Create and run server
    mcp = create_server()
    logger.info("MCP server created successfully. Starting server...")

    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()