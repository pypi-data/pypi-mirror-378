#!/usr/bin/env python3
"""Main entry point for the Akto Gateway."""

import asyncio
import json
import os
import signal
import sys
from typing import List

from .constants import DEFAULT_API_BASE_URL
from .session import SessionManager
from .transport import create_stdio_transport_and_execute


def print_help():
    """Print help information."""
    print("Akto MCP Wrapper - Threat Detection and Discovery")
    print("=" * 50)
    print()
    print("Usage:")
    print("  akto-mcp-wrapper stdio --name <name> [--akto-api-token <token>] --exec <command>")
    print()
    print("Commands:")
    print("  stdio     Run as MCP stdio wrapper")
    print("  help      Show this help")
    print()
    print("Options:")
    print("  --name <name>                  Project name for session tracking")
    # API base URL is fixed to default; no CLI override
    print("  --akto-api-token <token>       API key for authentication (defaults to AKTO_API_TOKEN env var)")
    print("  --env KEY=VALUE        Environment variable to pass to MCP server subprocess")
    print("  --exec <command>       MCP server command to execute")
    print()
    print("Examples:")
    print("  akto-mcp-wrapper stdio --name my-project --exec 'uv run server.py'")
    print("  akto-mcp-wrapper stdio --name vul-security --akto-api-token mytoken --exec 'python vul_mcp.py'")
    print()
    print("Features:")
    print("  ✅ MCP Protocol Interception")
    print("  ✅ Request/Response Validation APIs")
    print("  ✅ Data Ingestion")
    print("  ✅ Session Tracking")
    print("  📊 Comprehensive Logging")


def parse_arguments(args: List[str]):
    """Parse command line arguments."""
    project_name = None
    log_dir = None
    api_url = None
    api_key = None
    mcp_server_command_args = []
    env_vars = {}
    
    # First pass: collect all --env arguments
    i = 0
    while i < len(args):
        if args[i] == "--env" and i + 1 < len(args):
            # Parse environment variables in format KEY=VALUE
            env_key_value = args[i + 1]
            if '=' in env_key_value:
                key, value = env_key_value.split('=', 1)
                env_vars[key] = value
            i += 2
        else:
            i += 1
    
    # Second pass: parse other arguments and find --exec
    i = 0
    while i < len(args):
        if args[i] == "--name" and i + 1 < len(args):
            project_name = args[i + 1]
            i += 2
        elif args[i] == "--log-dir" and i + 1 < len(args):
            log_dir = args[i + 1]
            i += 2
        elif args[i] == "--akto-api-token" and i + 1 < len(args):
            api_key = args[i + 1]
            i += 2
        elif args[i] == "--env":
            # Skip --env arguments as they're already processed
            i += 2
        elif args[i] == "--exec":
            # Collect all remaining arguments as the command, but filter out --env arguments
            remaining_args = args[i + 1:]
            mcp_server_command_args = []
            j = 0
            while j < len(remaining_args):
                if remaining_args[j] == "--env" and j + 1 < len(remaining_args):
                    # Skip --env arguments as they're already processed
                    j += 2
                else:
                    mcp_server_command_args.append(remaining_args[j])
                    j += 1
            break
        else:
            i += 1
    
    return project_name, log_dir, api_url, api_key, mcp_server_command_args, env_vars


async def run_mcp_gateway(project_name: str, api_url: str, api_key: str, mcp_server_command_args: List[str], env_vars: dict = None):
    """Run the MCP gateway."""
    if not mcp_server_command_args:
        print("Error: No MCP server command specified after --exec")
        return 1
    
    json_log = {
        "event": "gateway_startup",
        "message": "Starting Akto Gateway...",
        "details": {
            "project": project_name,
            "api_url": api_url,
            "api_key": "***" if api_key else "None",
            "mcp_server": " ".join(mcp_server_command_args)
        }
    }
    sys.stdout.write(f"{json.dumps(json_log)}\n")
    print()
    
    # Initialize components
    session_manager = SessionManager()
    
    try:
        # Start the gateway
        await create_stdio_transport_and_execute(
            session_manager=session_manager,
            project_name=project_name,
            mcp_server_command_args=mcp_server_command_args,
            api_base_url=api_url,
            api_key=api_key,
            env_vars=env_vars,
        )
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main entry point."""
    # Handle signals for graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if len(sys.argv) < 2:
        print("Error: No command specified")
        print_help()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "help":
        print_help()
        return 0
    
    elif command == "stdio":
        if len(sys.argv) < 3:
            print("Error: Missing required arguments for stdio command")
            print_help()
            return 1
        
        # Parse arguments
        project_name, log_dir, api_url, api_key, mcp_server_command_args, env_vars = parse_arguments(sys.argv[2:])
        
        if not project_name:
            print("Error: --name is required")
            print_help()
            return 1
        
        if not mcp_server_command_args:
            print("Error: --exec is required")
            print_help()
            return 1
        
        # Set defaults
        if not log_dir:
            log_dir = "./logs"
        if not api_url:
            api_url = DEFAULT_API_BASE_URL
        
        # Get API key from environment variable if not provided via command line
        if not api_key:
            api_key = os.getenv("AKTO_API_TOKEN")
            if not api_key:
                print("Error: AKTO_API_TOKEN environment variable is not set")
                print_help()
                return 1       

        print(f"env_vars: {env_vars}")
        # Run the gateway
        return asyncio.run(run_mcp_gateway(
            project_name=project_name,
            api_url=api_url,
            api_key=api_key,
            mcp_server_command_args=mcp_server_command_args,
            env_vars=env_vars
        ))
    
    else:
        print(f"Error: Unknown command: {command}")
        print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
