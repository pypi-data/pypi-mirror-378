# NTHU Complaints MCP 2.0.1

[![PyPI version](https://badge.fury.io/py/nthu-complaints-mcp.svg)](https://badge.fury.io/py/nthu-complaints-mcp)
[![Python Support](https://img.shields.io/pypi/pyversions/nthu-complaints-mcp.svg)](https://pypi.org/project/nthu-complaints-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**NTHU Complaints MCP Server** - 一個功能強大的 Model Context Protocol (MCP) 伺服器，專為測試和互動清華大學申訴系統 API 而設計。

## 🚀 特色功能

- **🛠️ 完整的 API 測試工具** - 提供全面的申訴系統 API 測試功能
- **🔧 Model Context Protocol 支援** - 標準化的 MCP 工具接口
- **⚡ 異步處理** - 高效能的異步 HTTP 請求處理
- **🎯 類型安全** - 使用 Pydantic 進行資料驗證和類型檢查
- **🖥️ 友善的 CLI** - 豐富的命令列界面，支援多種操作模式
- **📊 詳細的測試報告** - 完整的測試結果和錯誤報告
- **🔌 即插即用** - 易於安裝和配置

## 📦 安裝

### 使用 pip 安裝

```bash
pip install nthu-complaints-mcp
```

### 使用 uvx 運行（推薦）

```bash
uvx nthu-complaints-mcp serve
```

### 從源碼安裝

```bash
git clone https://github.com/nthu-complaints/nthu-complaints-mcp.git
cd nthu-complaints-mcp
pip install -e .
```

## 🏃‍♂️ 快速開始

### 1. 啟動 MCP 伺服器

```bash
# 使用預設設定啟動
nthu-complaints-mcp serve

# 自訂 API 基礎 URL
nthu-complaints-mcp serve --base-url https://your-api-url.com/.netlify/functions

# 啟用除錯模式
nthu-complaints-mcp serve --debug
```

### 2. 執行快速連線測試

```bash
nthu-complaints-mcp test
```

### 3. 查看詳細資訊

```bash
nthu-complaints-mcp info
```

## 🛠️ 可用工具

### 申訴相關工具

#### `test_submit_complaint`
測試申訴提交功能

```python
# 參數
email: str = "test@example.com"           # 用戶電子郵件
name: str = "測試用戶"                    # 用戶姓名
complaint_type: str = "academic_rules"   # 申訴類型
complaint_details: str = "申訴詳情"      # 申訴內容
expected_action: str = "期望處理方式"    # 期望的處理方式
phone: Optional[str] = None               # 聯絡電話（可選）
student_id: Optional[str] = None          # 學號（可選）
department: Optional[str] = None          # 科系（可選）
```

#### `test_track_complaint`
測試申訴追蹤功能

```python
# 參數
case_number: str                          # 案件編號
verification_code: str                    # 驗證碼
user_id: str = "test-user-123"           # 用戶ID
```

#### `test_get_complaint_details`
測試申訴詳情查詢功能

```python
# 參數
case_number: str                          # 案件編號
verification_code: str                    # 驗證碼
```

### 系統工具

#### `check_api_connection`
檢查 API 連線狀態

#### `run_full_api_test`
執行完整的 API 測試流程

```python
# 參數
email: str = "test@example.com"           # 測試用戶電子郵件
name: str = "測試用戶"                    # 測試用戶姓名
```

## 📋 申訴類型

支援的申訴類型：

- `academic_rules` - 學術規則相關
- `administrative` - 行政程序相關
- `facilities` - 設施設備相關
- `other` - 其他類型

## 🔧 使用範例

### Python 程式碼範例

```python
from nthu_complaints_mcp import NTHUComplaintsMCP

# 創建伺服器實例
server = NTHUComplaintsMCP(
    base_url="https://your-api-url.com/.netlify/functions"
)

# 啟動伺服器
server.run()
```

### MCP 客戶端使用

當伺服器運行後，您可以透過任何支援 MCP 的客戶端連接並使用這些工具：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "test_submit_complaint",
    "arguments": {
      "email": "student@nthu.edu.tw",
      "name": "張三",
      "complaint_type": "academic_rules",
      "complaint_details": "關於課程安排的申訴",
      "expected_action": "希望重新安排課程時間"
    }
  }
}
```

## 🏗️ 專案結構

```
nthu-complaints-mcp/
├── nthu_complaints_mcp/
│   ├── __init__.py          # 套件初始化
│   ├── server.py            # 主要伺服器實作
│   ├── models.py            # 資料模型定義
│   ├── exceptions.py        # 例外處理類別
│   └── cli.py              # 命令列介面
├── tests/                   # 測試檔案
├── pyproject.toml          # 專案配置
├── README.md               # 專案說明
└── LICENSE                 # 授權條款
```

## 🧪 開發與測試

### 安裝開發依賴

```bash
pip install -e ".[dev]"
```

### 執行測試

```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/test_server.py

# 生成覆蓋率報告
pytest --cov=nthu_complaints_mcp
```

### 程式碼格式化

```bash
# 格式化程式碼
black nthu_complaints_mcp/
isort nthu_complaints_mcp/

# 檢查程式碼風格
flake8 nthu_complaints_mcp/
mypy nthu_complaints_mcp/
```

## 📚 API 文件

### 回應格式

所有工具都會回傳統一格式的結果：

```python
{
    "success": bool,              # 操作是否成功
    "status_code": int,           # HTTP 狀態碼（如適用）
    "message": str,               # 操作結果訊息
    "data": dict,                 # 回應資料（如適用）
    "error": str,                 # 錯誤訊息（如有錯誤）
    "execution_time": float,      # 執行時間（秒）
    "timestamp": datetime         # 時間戳記
}
```

### 錯誤處理

套件提供完善的錯誤處理機制：

- `NTHUComplaintsError` - 基礎例外類別
- `APIConnectionError` - API 連線錯誤
- `ValidationError` - 資料驗證錯誤
- `AuthenticationError` - 身份驗證錯誤
- `ComplaintNotFoundError` - 申訴案件不存在
- `RateLimitError` - API 請求限制

## 🤝 貢獻指南

我們歡迎社群貢獻！請閱讀我們的貢獻指南：

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案。

## 🆘 支援與問題回報

- **GitHub Issues**: [問題回報](https://github.com/nthu-complaints/nthu-complaints-mcp/issues)
- **電子郵件**: complaints@nthu.edu.tw
- **文件**: [線上文件](https://github.com/nthu-complaints/nthu-complaints-mcp#readme)

## 📈 更新日誌

### v2.0.1 (2024-12-19)

- 🎉 全新的 MCP 2.0 架構
- ⚡ 改善的效能和穩定性
- 🛠️ 新增豐富的 CLI 工具
- 📊 完整的測試覆蓋率
- 🔧 更好的錯誤處理機制
- 📚 完整的 API 文件

---

**由清華大學申訴系統團隊開發維護** 🎓