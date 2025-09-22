"""Constants for the Akto MCP Gateway."""

# MCP Message Types
MCP_METHOD = "method"
MCP_TOOL_CALL = "tools/call"
MCP_LIST_TOOLS = "tools/list"
MCP_PARAMS = "params"
MCP_RESULT = "result"
MCP_SERVER_INFO = "serverInfo"
MCP_CLIENT_INFO = "clientInfo"

# Session Management
SESSION_ID_PREFIX = "akto-"
UTF_8 = "utf-8"

# Logging
DEFAULT_LOG_DIR = "./logs"
MCP_MESSAGES_LOG = "mcp_messages.log"
MCP_SESSIONS_LOG = "mcp_sessions.log"
MCP_ERRORS_LOG = "mcp_errors.log"
MCP_INFO_LOG = "mcp_info.log"
MCP_BLOCKED_LOG = "mcp_blocked.log"
MCP_RAW_STDOUT_LOG = "mcp_raw_stdout.log"

# PII patterns for detection
PII_PATTERNS = {
    "phone": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    "mac_address": r'\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b',
    "api_key": r'\b(?:sk-[a-zA-Z0-9]{10,}|pk_[a-zA-Z0-9]{10,})\b',
    "password": r'\b(?:password|passwd|pwd)[\s]*[=:]\s*[\w\-._~:/?#[\]@!$&\'()*+,;=%]+\b'
}

# High-risk PII patterns (always blocked)
HIGH_RISK_PII_PATTERNS = {
    "phone": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    "api_key": r'\b(?:sk-[a-zA-Z0-9]{10,}|pk_[a-zA-Z0-9]{10,})\b',
    "password": r'\b(?:password|passwd|pwd)[\s]*[=:]\s*[\w\-._~:/?#[\]@!$&\'()*+,;=%]+\b'
}

# Generic blocked response
BLOCKED_RESPONSE = {
    "jsonrpc": "2.0",
    "id": None,
    "error": {
        "code": -32000,
        "message": "Request blocked due to security policy",
        "data": {
            "reason": "PII or sensitive data detected",
            "blocked_at": None
        }
    }
}

# API Configuration
DEFAULT_API_BASE_URL = "http://localhost:9090"
DEFAULT_API_TIMEOUT = 30
