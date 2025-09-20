"""
NTHU Complaints MCP Server

Main server implementation using FastMCP framework for providing
Model Context Protocol tools for NTHU complaint system testing.
"""

import asyncio
import sys
import time
from typing import Dict, Any, Optional
import httpx
import fastmcp
from fastmcp import FastMCP

from .models import (
    ComplaintSubmission,
    ComplaintTracker,
    ComplaintDetails,
    APITestResult,
    FullTestResult,
    ComplaintType,
)
from .exceptions import (
    APIConnectionError,
    ValidationError,
    ComplaintNotFoundError,
)


class NTHUComplaintsMCP:
    """NTHU Complaints MCP Server implementation."""

    def __init__(self, base_url: str = None):
        """
        Initialize the MCP server.

        Args:
            base_url: Base URL for the NTHU complaints API
        """
        try:
            print("🔧 Initializing NTHU Complaints MCP Server...", file=sys.stderr)

            self.base_url = base_url or "https://deluxe-stardust-23afe0.netlify.app/.netlify/functions"
            print(f"🔗 Using base URL: {self.base_url}", file=sys.stderr)

            self.mcp = FastMCP("NTHU Complaints API Tester")
            print("📦 FastMCP instance created", file=sys.stderr)

            self._setup_tools()
            print("🛠️  Tools setup completed", file=sys.stderr)

        except Exception as e:
            print(f"❌ Error during initialization: {e}", file=sys.stderr)
            import traceback
            print(f"🐛 Traceback: {traceback.format_exc()}", file=sys.stderr)
            raise

    def _setup_tools(self) -> None:
        """Setup all MCP tools."""

        @self.mcp.tool()
        async def test_submit_complaint(
            email: str = "test@example.com",
            name: str = "測試用戶",
            complaint_type: str = "academic_rules",
            complaint_details: str = "這是一個測試申訴案件",
            expected_action: str = "希望得到回覆",
            phone: Optional[str] = None,
            student_id: Optional[str] = None,
            department: Optional[str] = None,
        ) -> Dict[str, Any]:
            """
            測試提交申訴 API

            Args:
                email: 用戶電子郵件
                name: 用戶姓名
                complaint_type: 申訴類型 (academic_rules, administrative, facilities, other)
                complaint_details: 申訴詳情
                expected_action: 期望的處理方式
                phone: 聯絡電話 (可選)
                student_id: 學號 (可選)
                department: 科系 (可選)

            Returns:
                API 回應結果
            """
            try:
                # Validate input
                submission = ComplaintSubmission(
                    email=email,
                    name=name,
                    complaint_type=ComplaintType(complaint_type),
                    complaint_details=complaint_details,
                    expected_action=expected_action,
                    phone=phone,
                    student_id=student_id,
                    department=department,
                )

                start_time = time.time()

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/submitComplaint",
                        json={
                            "email": submission.email,
                            "name": submission.name,
                            "complaintType": submission.complaint_type.value,
                            "complaintDetails": submission.complaint_details,
                            "expectedAction": submission.expected_action,
                            "phone": submission.phone,
                            "studentId": submission.student_id,
                            "department": submission.department,
                        },
                        timeout=30.0,
                    )

                execution_time = time.time() - start_time
                result = response.json()

                return APITestResult(
                    success=True,
                    status_code=response.status_code,
                    message="✅ 申訴提交測試完成",
                    data=result,
                    execution_time=execution_time,
                ).dict()

            except Exception as e:
                return APITestResult(
                    success=False,
                    message="❌ 申訴提交測試失敗",
                    error=str(e),
                ).dict()

        @self.mcp.tool()
        async def test_track_complaint(
            case_number: str,
            verification_code: str,
            user_id: str = "test-user-123",
        ) -> Dict[str, Any]:
            """
            測試追蹤申訴 API

            Args:
                case_number: 案件編號
                verification_code: 驗證碼
                user_id: 用戶ID

            Returns:
                API 回應結果
            """
            try:
                # Validate input
                tracker = ComplaintTracker(
                    case_number=case_number,
                    verification_code=verification_code,
                    user_id=user_id,
                )

                start_time = time.time()

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/trackComplaint",
                        json={
                            "caseNumber": tracker.case_number,
                            "verificationCode": tracker.verification_code,
                            "userId": tracker.user_id,
                        },
                        timeout=30.0,
                    )

                execution_time = time.time() - start_time
                result = response.json()

                return APITestResult(
                    success=True,
                    status_code=response.status_code,
                    message="✅ 申訴追蹤測試完成",
                    data=result,
                    execution_time=execution_time,
                ).dict()

            except Exception as e:
                return APITestResult(
                    success=False,
                    message="❌ 申訴追蹤測試失敗",
                    error=str(e),
                ).dict()

        @self.mcp.tool()
        async def test_get_complaint_details(
            case_number: str, verification_code: str
        ) -> Dict[str, Any]:
            """
            測試獲取申訴詳情 API

            Args:
                case_number: 案件編號
                verification_code: 驗證碼

            Returns:
                API 回應結果
            """
            try:
                # Validate input
                details = ComplaintDetails(
                    case_number=case_number, verification_code=verification_code
                )

                start_time = time.time()

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/getComplaintDetails",
                        json={
                            "caseNumber": details.case_number,
                            "verificationCode": details.verification_code,
                        },
                        timeout=30.0,
                    )

                execution_time = time.time() - start_time
                result = response.json()

                return APITestResult(
                    success=True,
                    status_code=response.status_code,
                    message="✅ 申訴詳情獲取測試完成",
                    data=result,
                    execution_time=execution_time,
                ).dict()

            except Exception as e:
                return APITestResult(
                    success=False,
                    message="❌ 申訴詳情獲取測試失敗",
                    error=str(e),
                ).dict()

        @self.mcp.tool()
        async def check_api_connection() -> Dict[str, Any]:
            """
            檢查 API 連接狀態

            Returns:
                連接狀態結果
            """
            try:
                start_time = time.time()

                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://deluxe-stardust-23afe0.netlify.app/", timeout=10.0
                    )

                execution_time = time.time() - start_time

                return APITestResult(
                    success=True,
                    status_code=response.status_code,
                    message="✅ API 連接正常",
                    data={"base_url": self.base_url},
                    execution_time=execution_time,
                ).dict()

            except Exception as e:
                return APITestResult(
                    success=False,
                    message="❌ 無法連接到 API",
                    error=str(e),
                    data={"suggestion": "請檢查網路連接或確認 Netlify Functions 服務正常運行"},
                ).dict()

        @self.mcp.tool()
        async def run_full_api_test(
            email: str = "test@example.com", name: str = "測試用戶"
        ) -> Dict[str, Any]:
            """
            執行完整的 API 測試流程

            Args:
                email: 測試用戶電子郵件
                name: 測試用戶姓名

            Returns:
                完整測試結果
            """
            start_time = time.time()
            results = FullTestResult(
                test_summary="NTHU Complaints API 完整測試",
                tests=[],
                overall_success=True,
                message="",
            )

            try:
                # 1. 檢查連接
                print("🔌 檢查 API 連接...")
                connection_result = await check_api_connection()
                results.tests.append({"name": "API 連接檢查", "result": connection_result})

                if not connection_result["success"]:
                    results.overall_success = False
                    results.message = "❌ API 連接失敗"
                    return results.dict()

                # 2. 提交申訴
                print("📝 測試申訴提交...")
                submit_result = await test_submit_complaint(email=email, name=name)
                results.tests.append({"name": "申訴提交測試", "result": submit_result})

                if not submit_result["success"]:
                    results.overall_success = False
                    results.message = "❌ 申訴提交失敗"
                    return results.dict()

                # 提取案件編號和驗證碼
                submit_data = submit_result.get("data", {})
                case_number = submit_data.get("caseNumber")
                verification_code = submit_data.get("verificationCode")

                if not case_number or not verification_code:
                    results.overall_success = False
                    results.message = "❌ 無法從申訴提交回應中獲取案件編號或驗證碼"
                    return results.dict()

                # 3. 追蹤申訴
                print("🔍 測試申訴追蹤...")
                track_result = await test_track_complaint(case_number, verification_code)
                results.tests.append({"name": "申訴追蹤測試", "result": track_result})

                if not track_result["success"]:
                    results.overall_success = False

                # 4. 獲取詳情
                print("📋 測試申訴詳情獲取...")
                details_result = await test_get_complaint_details(case_number, verification_code)
                results.tests.append({"name": "申訴詳情獲取測試", "result": details_result})

                if not details_result["success"]:
                    results.overall_success = False

                # 設置最終訊息
                if results.overall_success:
                    results.message = "🎉 所有 API 測試完成！微服務運行正常。"
                else:
                    results.message = "⚠️ 部分 API 測試失敗，請檢查具體錯誤。"

            except Exception as e:
                results.overall_success = False
                results.error = f"測試執行過程中發生錯誤: {str(e)}"
                results.message = "❌ API 測試執行失敗"

            finally:
                results.total_execution_time = time.time() - start_time

            return results.dict()

    def run(self) -> None:
        """Run the MCP server."""
        try:
            print("🚀 Starting NTHU Complaints MCP Server...", file=sys.stderr)
            print(f"📦 FastMCP version: {fastmcp.__version__}", file=sys.stderr)
            print(f"🔗 Base URL: {self.base_url}", file=sys.stderr)
            print(f"🛠️  Tools registered: {len(self.mcp._tools)}", file=sys.stderr)
            print("✅ Server initialization complete", file=sys.stderr)

            self.mcp.run()
        except Exception as e:
            print(f"❌ Server error in run(): {e}", file=sys.stderr)
            import traceback
            print(f"🐛 Traceback: {traceback.format_exc()}", file=sys.stderr)
            raise


def create_server(base_url: str = None) -> NTHUComplaintsMCP:
    """
    Factory function to create a new NTHU Complaints MCP server.

    Args:
        base_url: Base URL for the NTHU complaints API

    Returns:
        Configured NTHUComplaintsMCP instance
    """
    return NTHUComplaintsMCP(base_url=base_url)