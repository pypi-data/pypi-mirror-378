import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .constants import (
    DEFAULT_LOG_DIR,
    MCP_MESSAGES_LOG,
    MCP_SESSIONS_LOG,
    MCP_ERRORS_LOG,
    MCP_INFO_LOG,
    MCP_BLOCKED_LOG,
    MCP_RAW_STDOUT_LOG,
)


class AktoLogger:
    """Centralized logging utility for the Akto Gateway."""
    
    def __init__(self, log_dir: str = DEFAULT_LOG_DIR, verbose: bool = False):
        self.log_dir = Path(log_dir)
        self.verbose = verbose
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup loggers
        self._setup_loggers()
    
    def _setup_loggers(self):
        """Setup all the loggers."""
        # Make logger names unique per log_dir to avoid handler overlap across instances
        logger_suffix = str(self.log_dir)

        # Messages logger
        self.messages_logger = logging.getLogger(f"mcp_messages:{logger_suffix}")
        self.messages_logger.setLevel(logging.INFO)
        self.messages_logger.propagate = False
        self.messages_logger.handlers.clear()
        messages_handler = logging.FileHandler(self.log_dir / MCP_MESSAGES_LOG)
        messages_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.messages_logger.addHandler(messages_handler)
        
        # Sessions logger (no file output)
        self.sessions_logger = logging.getLogger(f"mcp_sessions:{logger_suffix}")
        self.sessions_logger.setLevel(logging.INFO)
        self.sessions_logger.propagate = False
        self.sessions_logger.handlers.clear()
        
        # Errors logger
        self.errors_logger = logging.getLogger(f"mcp_errors:{logger_suffix}")
        self.errors_logger.setLevel(logging.ERROR)
        self.errors_logger.propagate = False
        self.errors_logger.handlers.clear()
        errors_handler = logging.FileHandler(self.log_dir / MCP_ERRORS_LOG)
        errors_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.errors_logger.addHandler(errors_handler)

        # Raw stdout logger: captures non-JSON lines from MCP server
        self.raw_stdout_logger = logging.getLogger(f"mcp_raw_stdout:{logger_suffix}")
        self.raw_stdout_logger.setLevel(logging.INFO)
        self.raw_stdout_logger.propagate = False
        self.raw_stdout_logger.handlers.clear()
        raw_handler = logging.FileHandler(self.log_dir / MCP_RAW_STDOUT_LOG)
        raw_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.raw_stdout_logger.addHandler(raw_handler)
        
        # Info logger (no file output)
        self.info_logger = logging.getLogger(f"mcp_info:{logger_suffix}")
        self.info_logger.setLevel(logging.INFO)
        self.info_logger.propagate = False
        self.info_logger.handlers.clear()
        
        # Blocked requests logger (no file output)
        self.blocked_logger = logging.getLogger(f"mcp_blocked:{logger_suffix}")
        self.blocked_logger.setLevel(logging.WARNING)
        self.blocked_logger.propagate = False
        self.blocked_logger.handlers.clear()
        
        # Console logger for verbose output
        if self.verbose:
            console_handler = logging.StreamHandler(stream=sys.stderr)
            console_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.messages_logger.addHandler(console_handler)
            self.sessions_logger.addHandler(console_handler)
            self.errors_logger.addHandler(console_handler)
            self.info_logger.addHandler(console_handler)
            self.blocked_logger.addHandler(console_handler)
            self.raw_stdout_logger.addHandler(console_handler)
    
    def log_message(self, direction: str, message: Dict[str, Any], session_id: str):
        """Log an MCP message."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "session_id": session_id,
            "direction": direction,  # "client->server" or "server->client"
            "message": message
        }
        
        self.messages_logger.info(json.dumps(log_entry))
        
        if self.verbose:
            sys.stderr.write(f"[{timestamp}] {direction} - Session: {session_id}\n")
            sys.stderr.write(f"  Method: {message.get('method', 'unknown')}\n")
            sys.stderr.write(f"  ID: {message.get('id', 'unknown')}\n")
    
    def log_session(self, session_id: str, action: str, details: str = ""):
        """Log session-related events."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "session_id": session_id,
            "action": action,
            "details": details
        }
        
        self.sessions_logger.info(json.dumps(log_entry))
        
        if self.verbose:
            sys.stderr.write(f"[{timestamp}] Session {action}: {session_id}\n")
            if details:
                sys.stderr.write(f"  Details: {details}\n")
    
    def log_error(self, error: str, session_id: str = "", details: str = ""):
        """Log errors."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "session_id": session_id,
            "error": error,
            "details": details
        }
        
        self.errors_logger.error(json.dumps(log_entry))
        
        if self.verbose:
            sys.stderr.write(f"[{timestamp}] ERROR - Session: {session_id or 'unknown'}\n")
            sys.stderr.write(f"  Error: {error}\n")
            if details:
                sys.stderr.write(f"  Details: {details}\n")
    
    def log_info(self, message: str, session_id: str = "", details: str = ""):
        """Log general info messages."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "session_id": session_id,
            "info": message,
            "details": details
        }
        
        self.info_logger.info(json.dumps(log_entry))
        
        if self.verbose:
            sys.stderr.write(f"[{timestamp}] INFO - Session: {session_id or 'unknown'}\n")
            sys.stderr.write(f"  Info: {message}\n")
            if details:
                sys.stderr.write(f"  Details: {details}\n")

    def log_raw_stdout(self, line: bytes):
        """Log raw non-JSON stdout from MCP server to a separate file."""
        try:
            text = line.decode('utf-8', errors='replace').rstrip('\n')
        except Exception:
            text = str(line)
        self.raw_stdout_logger.info(text)
    
    def log_blocked(self, request: Dict[str, Any], detected_pii: List[Dict[str, Any]], 
                    session_id: str, direction: str = "request"):
        """Log blocked requests due to PII detection."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "session_id": session_id,
            "direction": direction,
            "request": request,
            "detected_pii": detected_pii,
            "blocked_at": timestamp
        }
        
        self.blocked_logger.warning(json.dumps(log_entry))
        
        if self.verbose:
            sys.stderr.write(f"[{timestamp}] BLOCKED - Session: {session_id}\n")
            sys.stderr.write(f"  Direction: {direction}\n")
            sys.stderr.write(f"  PII Detected: {len(detected_pii)} items\n")
            for pii in detected_pii:
                sys.stderr.write(f"    - {pii['type']}: {pii['value']} ({pii.get('context', 'unknown')})\n")
