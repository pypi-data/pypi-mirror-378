import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional


class McpSession:
    """Represents an MCP session with message tracking."""
    
    def __init__(self, session_id: str, project_name: str):
        self.session_id = session_id
        self.project_name = project_name
        self.created_at = datetime.now().isoformat()
        self.last_activity = self.created_at
        self.messages: List[Dict[str, Any]] = []
        self.client_info: Optional[Dict[str, Any]] = None
        self.server_info: Optional[Dict[str, Any]] = None
    
    def add_message(self, message: Dict[str, Any], direction: str):
        """Add a message to the session."""
        self.messages.append({
            "timestamp": datetime.now().isoformat(),
            "direction": direction,
            "message": message
        })
        self.last_activity = datetime.now().isoformat()
    
    def update_client_info(self, client_info: Dict[str, Any]):
        """Update client information."""
        self.client_info = client_info
    
    def update_server_info(self, server_info: Dict[str, Any]):
        """Update server information."""
        self.server_info = server_info
    
    def get_corresponding_request(self, response_id: Any) -> Optional[Dict[str, Any]]:
        """Find the most recent request that matches the given response ID."""
        if response_id is None:
            return None
        
        # Look for the most recent client->server message with matching ID
        for message in reversed(self.messages):
            if (message["direction"] == "client->server" and 
                message["message"].get("id") == response_id):
                return message["message"]
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "project_name": self.project_name,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "message_count": len(self.messages),
            "client_info": self.client_info,
            "server_info": self.server_info
        }


class SessionManager:
    """Manages MCP sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, McpSession] = {}
    
    def create_session(self, project_name: str) -> str:
        """Create a new session."""
        session_id = f"akto-{uuid.uuid4().hex[:12]}"
        session = McpSession(session_id, project_name)
        self.sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Optional[McpSession]:
        """Get a session by ID."""
        return self.sessions.get(session_id)
    
    def get_all_sessions(self) -> List[McpSession]:
        """Get all sessions."""
        return list(self.sessions.values())
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old sessions."""
        cutoff = datetime.now().timestamp() - (max_age_hours * 3600)
        
        sessions_to_remove = []
        for session_id, session in self.sessions.items():
            session_timestamp = datetime.fromisoformat(session.last_activity).timestamp()
            if session_timestamp < cutoff:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
