import asyncio
import aiohttp
import json
from typing import Any, Dict, Optional, Tuple


class AktoAPIClient:
    """API client for Akto validation and ingestion services."""
    
    def __init__(self, 
                 base_url: str,
                 api_key: Optional[str] = None,
                 timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout
            )
        return self._session
    
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def validate_request(self, request_data: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate request before sending to MCP server.
        
        Args:
            request_data: JSON string of the request
            
        Returns:
            Tuple[bool, Optional[Dict]]: (is_allowed, response_data)
            - is_allowed: True if request should proceed, False if blocked
            - response_data: The response from validate API (None if request fails)
        """
        try:
            session = await self._get_session()
            payload = {
                "request": request_data
            }
            
            url = f"{self.base_url}/validateRequest"
            async with session.post(url, json=payload) as response:
                response_data = await response.json()
                
                # API call completed successfully
                
                # Check if response indicates blocking
                is_allowed = self._is_request_allowed(response_data)
                
                return is_allowed, response_data
                
        except Exception as e:
            # If API fails, allow the request to proceed (fail-open)
            return True, None
    
    async def validate_response(self, response_data: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate response after receiving from MCP server.
        
        Args:
            response_data: JSON string of the response
            
        Returns:
            Tuple[bool, Optional[Dict]]: (is_allowed, response_data)
            - is_allowed: True if response should be sent to client, False if blocked
            - response_data: The response from validate API (None if request fails)
        """
        try:
            session = await self._get_session()
            payload = {
                "response": response_data
            }
            
            url = f"{self.base_url}/validateResponse"
            async with session.post(url, json=payload) as response:
                response_data = await response.json()
                
                # API call completed successfully
                
                # Check if response indicates blocking
                is_allowed = self._is_request_allowed(response_data)
                
                return is_allowed, response_data
                
        except Exception as e:
            # If API fails, allow the response to proceed (fail-open)
            return True, None
    
    async def ingest_data(self, ingest_request_json: Dict[str, Any]) -> bool:
        """
        Call the ingest_data API with the pre-created ingest request JSON.
        
        Args:
            ingest_request_json: Pre-created ingest request JSON
            
        Returns:
            bool: True if ingestion succeeded, False otherwise
        """
        try:
            session = await self._get_session()
            
            url = f"{self.base_url}/api/ingestData"
            async with session.post(url, json=ingest_request_json) as response:
                response_data = await response.json()
                
                # API call completed successfully
                
                return response.status == 200
                
        except Exception as e:
            return False
    
    def _is_request_allowed(self, api_response: Dict[str, Any]) -> bool:
        """
        Check if the API response indicates the request should be allowed.
        
        Args:
            api_response: Response from validate API
            
        Returns:
            bool: True if allowed, False if blocked
        """
        # Check for common blocking indicators
        if not api_response:
            return True
        
        # Check for explicit block/allow flags
        if "block" in api_response:
            return not api_response["block"]
        
        if "allow" in api_response:
            return api_response["allow"]
        
        if "action" in api_response:
            action = api_response["action"].lower()
            return action not in ["block", "deny", "reject"]
        
        # Check for error conditions that might indicate blocking
        if "error" in api_response:
            error_code = api_response["error"].get("code")
            if error_code == -32000:  # Security policy error
                return False
        
        # Default to allowing if no clear blocking indicator
        return True
    
    def create_blocked_response(self, original_request_str: str, block_reason: str = "Request blocked due to security policy") -> Dict[str, Any]:
        """
        Create a standardized blocked response for the client.
        
        Args:
            original_request_str: JSON string of the original request that was blocked
            block_reason: Reason for blocking
            
        Returns:
            Dict: Standardized blocked response
        """
        try:
            original_request = json.loads(original_request_str)
            request_id = original_request.get("id")
        except (json.JSONDecodeError, TypeError):
            request_id = None
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32000,
                "message": block_reason,
                "data": {
                    "reason": "Request blocked by security policy",
                    "blocked_at": self._get_timestamp()
                }
            }
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
