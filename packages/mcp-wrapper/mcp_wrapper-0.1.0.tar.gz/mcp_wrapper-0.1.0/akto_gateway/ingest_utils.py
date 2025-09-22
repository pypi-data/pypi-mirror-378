import json
import time
from typing import Dict, Any, Optional

from .device_utils import get_machine_id



def generate_ingest_data(request_data: Dict[str, Any], 
                        response_data: Dict[str, Any],
                        project_name: str,
                        dest_ip: str = "127.0.0.1",
                        source_ip: str = "127.0.0.1") -> Dict[str, Any]:
    """
    Generate ingest_data JSON from MCP request and response.
    
    Args:
        request_data: MCP request data (dict)
        response_data: MCP response data (dict)
        dest_ip: Destination IP (default: 127.0.0.1)
        source_ip: Source IP (default: 127.0.0.1)
        
    Returns:
        Dict containing the batchData format for ingest_data API
    """        
    # Get machine ID from global state
    machine_id = get_machine_id()
    
    # Generate headers
    request_headers = _generate_request_headers(machine_id, project_name)
    
    # Determine status code and status
    status_code = "200"
    status = "200 OK"
    
    # Create the individual ingest data item
    ingest_item = {
        "destIp": dest_ip,
        "method": "POST",
        "requestPayload": json.dumps(request_data),
        "responsePayload": json.dumps(response_data),
        "ip": source_ip,
        "source": "MIRRORING",
        "path": "/mcp",
        "requestHeaders": request_headers,
        "responseHeaders": "",
        "time": int(time.time()),
        "statusCode": status_code,
        "status": status,
        "akto_account_id": "1000000",
        "type": "",
        "is_pending": "false",
        "tag": "",
        "akto_vxlan_id": "0"
    }
    
    # Return in batchData format
    return {
        "batchData": [ingest_item]
    }


def _generate_request_headers(machine_id: str, project_name: str) -> str:
    """Generate request headers JSON string."""
    headers = {
        "x-transport": "STDIO",
        "host": f"{machine_id}.{project_name}"
    }
    return json.dumps(headers)

