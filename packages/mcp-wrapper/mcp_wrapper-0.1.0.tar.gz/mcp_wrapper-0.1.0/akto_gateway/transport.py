import asyncio
import json
import signal
import sys
import os
import platform
import select
import subprocess
from typing import Any, Dict, Tuple, Optional
from .session import SessionManager
from .constants import UTF_8, DEFAULT_API_BASE_URL, DEFAULT_API_TIMEOUT
from .api_client import AktoAPIClient
from .ingest_utils import generate_ingest_data

class StdioTransport:
    """STDIO transport for MCP with API validation and data ingestion."""
    
    def __init__(self, session_manager: SessionManager, 
                 project_name: str, api_base_url: str = DEFAULT_API_BASE_URL,
                 api_key: Optional[str] = None,
                 api_timeout: int = DEFAULT_API_TIMEOUT):
        self.session_manager = session_manager
        self.project_name = project_name
        self.mcp_process: Optional[subprocess.Popen] = None
        
        # Initialize API client (generic HTTP client)
        self.api_client = AktoAPIClient(
            base_url=api_base_url,
            api_key=api_key,
            timeout=api_timeout
        )    
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def start_mcp_process(self, mcp_server_command_args: list, env_vars: dict = None) -> subprocess.Popen:
        """Start the MCP server subprocess."""
        
        print(f"Starting MCP server: {mcp_server_command_args}")
        # Use custom environment variables only if provided
        if env_vars:
            env = os.environ.copy()
            env.update(env_vars)
            self.mcp_process = subprocess.Popen(
                mcp_server_command_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0,
                env=env
            )
        else:
            self.mcp_process = subprocess.Popen(
                mcp_server_command_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0
            )
        print(f"MCP server started: {self.mcp_process}")
        print(f"MCP server PID: {self.mcp_process.pid}")
        print(f"MCP server returncode: {self.mcp_process.returncode}")
        
        return self.mcp_process
    
    async def handle_communication(self, session_id: str, mcp_process: subprocess.Popen):
        """Handle stdio communication loop."""
        self.mcp_process = mcp_process
        print(f"Starting communication loop for session: {session_id}")
        print(f"Process status: running={mcp_process.poll() is None}, returncode={mcp_process.returncode}")

        # Start async tasks for stdout and stderr
        stdout_task = asyncio.create_task(self._stream_and_forward_stdout(session_id))
        #stderr_task = asyncio.create_task(self._stream_and_forward_stderr())
        
        try:
            print("Starting stdin input loop...")
            # Handle stdin input loop
            await self._run_stdio_input_loop(session_id)
            print("Stdin input loop completed")
        except Exception as e:
            print(f"Error in communication loop: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            # Cleanup
            if self.mcp_process and self.mcp_process.stdin:
                self.mcp_process.stdin.close()
            
            # Terminate process if needed
            if self.mcp_process and self.mcp_process.poll() is None:
                self.mcp_process.terminate()
                try:
                    await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, self.mcp_process.wait
                        ),
                        timeout=2,
                    )
                except asyncio.TimeoutError:
                    self.mcp_process.kill()
            
            # Cancel I/O tasks
            stdout_task.cancel()
            #stderr_task.cancel()
            
            # Close API client
            await self.api_client.close()
            
            # Final flush
            sys.stdout.flush()
    
    async def _stream_and_forward_stdout(self, session_id: str):
        """Read from MCP process stdout and forward to sys.stdout."""
        loop = asyncio.get_event_loop()
        
        while True:
            if self.mcp_process.poll() is not None:
                break
            
            line = await loop.run_in_executor(None, self.mcp_process.stdout.readline)
            if not line:
                break
            
            try:
                decoded_line = line.decode(UTF_8).strip()
                if not decoded_line:
                    continue
                
                # Try to parse for logging and session metadata; only forward valid JSON
                try:
                    response_body = json.loads(decoded_line)
                    session = self.session_manager.get_session(session_id)

                    # Validate response after receiving from MCP server
                    response_str = json.dumps(response_body)
                    try:
                        is_allowed, validation_response = await self.api_client.validate_response(response_str)
                    except Exception as e:
                        sys.stderr.write(f"[{self._get_timestamp()}] ERROR validate_response failed: {e}\n")
                        sys.stderr.flush()
                        # Fail-open: allow response to pass through on validation outage
                        is_allowed = True
                        validation_response = None

                    if not is_allowed:
                        # Response is blocked, send blocked response to client
                        blocked_response = self.api_client.create_blocked_response(response_str)

                        # Note: Not storing blocked responses in session as they're not needed for correlation

                        # Send blocked response to client
                        sys.stdout.buffer.write(self._serialize_to_bytes(blocked_response))
                        sys.stdout.buffer.flush()
                        continue

                    # Response is allowed, proceed with normal flow
                    if session:
                        # Only update server info if present, don't store response in session
                        if "result" in response_body and "serverInfo" in response_body["result"]:
                            session.update_server_info(response_body["result"]["serverInfo"])

                    # Get the corresponding request for data ingestion
                    request_body = None
                    if session:
                        # Find the most recent request that matches this response
                        request_body = session.get_corresponding_request(response_body.get("id"))

                    # Ingest data (request and response)
                    if request_body:
                        request_str = json.dumps(request_body)
                        try:
                            # Step 1: Create the ingest request JSON using the utility
                            ingest_request_json = generate_ingest_data(request_body, response_body, self.project_name)
                            
                            # Step 2: Call the ingest_data API with the created JSON
                            await self.api_client.ingest_data(ingest_request_json)
                        except Exception as e:
                            sys.stderr.write(f"[{self._get_timestamp()}] ERROR ingest_data failed: {e}\n")
                            sys.stderr.flush()

                except Exception:
                    # If not JSON, record raw line and DO NOT forward (parity with Invariant stdio)
                    continue
                
                # Forward normalized JSON to client
                sys.stdout.buffer.write(self._serialize_to_bytes(response_body))
                sys.stdout.buffer.flush()
                
            except Exception as e:
                sys.stderr.write(f"[{self._get_timestamp()}] ERROR processing MCP stdout: {e}\n")
                sys.stderr.flush()
                # Do not forward malformed/non-JSON lines
                continue
    
    async def _stream_and_forward_stderr(self):
        """Read from MCP process stderr and log it."""
        loop = asyncio.get_event_loop()
        
        while True:
            chunk = await loop.run_in_executor(
                None, lambda: self.mcp_process.stderr.read(10)
            )
            if not chunk:
                break
            
            # Log stderr as info (not errors) since stderr often contains normal startup messages
            try:
                stderr_text = chunk.decode(UTF_8)
                if stderr_text.strip():
                    sys.stdout.write(stderr_text)
                    sys.stdout.flush()
            except UnicodeDecodeError:
                # If we can't decode, just log the raw bytes as info
                try:
                    sys.stdout.buffer.write(chunk)
                    sys.stdout.flush()
                except Exception:
                    pass
    
    async def _run_stdio_input_loop(self, session_id: str):
        """Handle standard input, intercept calls and forward requests to MCP process stdin."""
        loop = asyncio.get_event_loop()
        stdin_fd = sys.stdin.fileno()
        buffer = b""
        
        # Set stdin to non-blocking mode
        os.set_blocking(stdin_fd, False)
        
        try:
            while True:
                # Get input using platform-specific method
                chunk, status = await self._wait_for_stdin_input(loop, stdin_fd)
                if status == "eof":
                    break
                elif status == "wait":
                    continue
                elif status == "data":
                    buffer += chunk
                    
                    # Process complete lines
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        if not line:
                            continue
                        
                        await self._process_stdin_line(session_id, line)
        
        except (BrokenPipeError, KeyboardInterrupt):
            pass
        finally:
            # Process any remaining data
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                if line:
                    await self._process_stdin_line(session_id, line)
    
    async def _process_stdin_line(self, session_id: str, line: bytes):
        """Process a line of input from stdin."""
        try:
            text = line.decode(UTF_8)
            request_body = json.loads(text)
        except json.JSONDecodeError as je:
            sys.stderr.write(f"[{self._get_timestamp()}] ERROR parsing stdin JSON: {je}\n")
            sys.stderr.flush()
            return
        
        # Validate request before sending to MCP server
        request_str = json.dumps(request_body)
        try:
            is_allowed, validation_response = await self.api_client.validate_request(request_str)
        except Exception as e:
            sys.stderr.write(f"[{self._get_timestamp()}] ERROR validate_request failed: {e}\n")
            sys.stderr.flush()
            # Fail-open on request validation outage
            is_allowed = True
            validation_response = None
        
        if not is_allowed:
            # Request is blocked, send blocked response to client
            blocked_response = self.api_client.create_blocked_response(request_str)
            
            # Store original request for potential logging/debugging
            session = self.session_manager.get_session(session_id)
            if session:
                session.add_message(request_body, "client->server")
            
            # Send blocked response to client
            sys.stdout.buffer.write(self._serialize_to_bytes(blocked_response))
            sys.stdout.buffer.flush()
            return
        
        # Request is allowed, proceed with normal flow
        # Add to session
        session = self.session_manager.get_session(session_id)
        if session:
            session.add_message(request_body, "client->server")
            
            # Update client info if available
            if "params" in request_body and "clientInfo" in request_body["params"]:
                session.update_client_info(request_body["params"]["clientInfo"])
        
        # Forward request to MCP server
        try:
            self.mcp_process.stdin.write(self._serialize_to_bytes(request_body))
            self.mcp_process.stdin.flush()
        except Exception as e:
            sys.stderr.write(f"[{self._get_timestamp()}] ERROR writing to MCP stdin: {e}\n")
            sys.stderr.flush()
            #add logging
    
    async def _wait_for_stdin_input(
        self, loop: asyncio.AbstractEventLoop, stdin_fd: int
    ) -> Tuple[bytes, str]:
        """Platform-specific implementation to wait for and read input from stdin."""
        if platform.system() == "Windows":
            await asyncio.sleep(0.01)
            try:
                chunk = await loop.run_in_executor(
                    None, lambda: os.read(stdin_fd, 4096)
                )
                if not chunk:
                    return None, "eof"
                return chunk, "data"
            except (BlockingIOError, OSError):
                return None, "wait"
        else:
            # Unix-like systems
            ready, _, _ = await loop.run_in_executor(
                None, lambda: select.select([stdin_fd], [], [], 0.1)
            )
            
            if not ready:
                await asyncio.sleep(0.01)
                return None, "wait"
            
            chunk = await loop.run_in_executor(None, lambda: os.read(stdin_fd, 4096))
            if not chunk:
                return None, "eof"
            return chunk, "data"
    
    def _serialize_to_bytes(self, data: dict) -> bytes:
        """Serialize dict to bytes using UTF-8 encoding."""
        return json.dumps(data).encode(UTF_8) + b"\n"


async def create_stdio_transport_and_execute(
    session_manager: SessionManager,
    project_name: str,
    mcp_server_command_args: list,
    api_base_url: str = DEFAULT_API_BASE_URL,
    api_key: Optional[str] = None,
    api_timeout: int = DEFAULT_API_TIMEOUT,
    env_vars: dict = None
):
    """Integration function for stdio execution."""
    stdio_transport = StdioTransport(
        session_manager=session_manager,
        project_name=project_name,
        api_base_url=api_base_url,
        api_key=api_key,
        api_timeout=api_timeout
    )
    
    # Create a new session
    session_id = session_manager.create_session(project_name)
    
    await stdio_transport.handle_communication(
        session_id=session_id,
        mcp_process=stdio_transport.start_mcp_process(mcp_server_command_args, env_vars),
    )
