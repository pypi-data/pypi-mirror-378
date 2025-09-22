"""
Agnost Analytics SDK for MCP Integration.

This module provides a client for tracking and analyzing MCP server interactions.
"""

import json
import time
import uuid
import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union, TypeVar, cast, Tuple, List
import requests
from datetime import datetime, timezone

from mcp import ListToolsResult, ServerResult, Tool
from mcp.server import Server
from mcp.types import CallToolRequest, ListToolsRequest, InitializeRequest
from mcp.shared.context import RequestContext
from .utils import is_fastmcp_server, is_mcp_error_response
from .types import AgnostConfig

# Set up logger
logger = logging.getLogger("agnost.analytics")
T = TypeVar('T')

class AgnostAnalytics:
    """
    Client for the Agnost MCP Analytics service.
    
    This class provides methods to track and analyze MCP server interactions.
    """

    def __init__(self) -> None:
        """Initialize the Agnost Analytics client."""
        self.endpoint: str = ""
        self.server: Optional[Any] = None
        self.org_id: Optional[str] = None
        self.session_ids: Dict[str, str] = {}
        self.initialized: bool = False
        self.config: Optional[AgnostConfig] = None

    def initialize(self, server: Any, org_id: str, config: AgnostConfig) -> bool:
        """
        Initialize the SDK and retrieve organization ID.
        
        Args:
            server: MCP server instance to track
            org_id: Organization ID for Agnost Analytics
            config: AgnostConfig instance
            
        Returns:
            bool: True if initialization was successful
        """
        if self.initialized:
            return True
        
        try:
            logger.debug("Initializing Agnost AI...")
            self.org_id = org_id
            self.endpoint = config.endpoint.rstrip('/')
            self.server = server
            self.config = config
            self.initialized = True

        except requests.exceptions.RequestException as e:
            return False
        except Exception as e:
            return False

        return True

    def _create_session_with_client_info(self, session_key: str, client_name: str) -> str:
        """Create a session with specific client info."""
        try:
            new_session_id = str(uuid.uuid4())
            response = requests.post(
                f"{self.endpoint}/capture-session",
                headers={
                    "Content-Type": "application/json",
                    "X-Org-Id": self.org_id or "",
                },
                json={
                    "session_id": new_session_id,
                    "client_config": client_name,
                    "connection_type": "",
                    "ip": "",
                },
                timeout=10
            )
            response.raise_for_status()
            self.session_ids[session_key] = new_session_id
            logger.debug(f"Session created with client info '{client_name}': {new_session_id}")
            return new_session_id
        except Exception as e:
            logger.warning(f"Failed to create session with client info: {e}")
            return ""

    def start_session(self, session_key: str, return_dummy_session: bool = False) -> str:
        """
        Start a new session for tracking events.

        Args:
            session_key: A key representing the session (e.g., a stringified id)

        Returns:
            str: A uuid4 generated session ID or empty string on failure
        """  
        if return_dummy_session:
            try:
                new_session_id = str(uuid.uuid4())
                response = requests.post(
                    f"{self.endpoint}/capture-session",
                    headers={
                        "Content-Type": "application/json",
                        "X-Org-Id": self.org_id or "",
                    },
                    json={
                        "session_id": new_session_id,
                        "client_config": "unidentified_client",
                        "connection_type": "",
                        "ip": "",  
                    },
                    timeout=10
                )
                response.raise_for_status()
                return new_session_id
            
            except Exception as e:
                logger.warning(f"Failed to start dummy session - unexpected error: {str(e)}")
                return ""

        if session_key in self.session_ids:
            return self.session_ids[session_key]     

        try:
            new_session_id = str(uuid.uuid4())
            config = "default"
            is_fastmcp = is_fastmcp_server(self.server)

            if is_fastmcp:
                try:
                    # For FastMCP, access context through the underlying MCP server
                    mcp_server = self.server._mcp_server
                    if hasattr(mcp_server, 'request_context') and mcp_server.request_context:
                        if hasattr(mcp_server.request_context, 'session') and mcp_server.request_context.session:
                            config = mcp_server.request_context.session.client_params.clientInfo.name
                        else:
                            logger.warning("FastMCP session not available")
                            config = "fastmcp_client"
                    else:
                        logger.warning("FastMCP request_context not available")
                        config = "fastmcp_client"
                except Exception as e:
                    logger.warning(f"Failed to get FastMCP client info: {e}")
                    config = "fastmcp_client"
            else:
                try:
                    # For low-level MCP servers, the server itself is the MCP server
                    if hasattr(self.server, '_mcp_server'):
                        lowlevel_server = self.server._mcp_server
                    else:
                        lowlevel_server = self.server

                    # Try multiple ways to access client info
                    if hasattr(lowlevel_server, 'request_context') and lowlevel_server.request_context:
                        if hasattr(lowlevel_server.request_context, 'session') and lowlevel_server.request_context.session:
                            config = lowlevel_server.request_context.session.client_params.clientInfo.name
                        else:
                            logger.warning("Low-level MCP request_context.session not available")
                            config = "lowlevel_no_session"
                    else:
                        logger.warning("Low-level MCP request_context not available")
                        config = "lowlevel_no_context"

                except Exception as e:
                    logger.warning(f"Failed to get lowlevel MCP client info: {e}")
                    config = "lowlevel_client"

            response = requests.post(
                f"{self.endpoint}/capture-session",
                headers={
                    "Content-Type": "application/json",
                    "X-Org-Id": self.org_id or "",
                },
                json={
                    "session_id": new_session_id,
                    "client_config": str(config),
                    "connection_type": "",
                    "ip": "",  
                },
                timeout=10
            )
            
            response.raise_for_status()
            self.session_ids[session_key] = new_session_id
            logger.debug(f"Session recorded: {new_session_id}")
            return new_session_id
        
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to start session - API error: {str(e)}")
            return ""
        except Exception as e:
            logger.warning(f"Failed to start session - unexpected error: {str(e)}")
            return ""
   
    def record_event(self, 
                     primitive_type: str, 
                     primitive_name: str, 
                     args: Any,
                     latency: int = 0,
                     success: bool = True,
                     result: Any = None) -> bool:
        """
        Record an event for analytics.

        Args:
            primitive_type: Type of primitive (tool/resource/prompt)
            primitive_name: Name of the primitive
            args: Arguments passed to the primitive
            latency: Execution time in milliseconds
            success: Whether the call was successful
            result: Output/result of the primitive call

        Returns:
            bool: True if recorded successfully, False otherwise
        """
        if not self.initialized or not self.server:
            logger.warning("AgnostAnalytics not initialized")
            return False
            
        try:
            try:
                if is_fastmcp_server(self.server):
                    # For FastMCP, access session through the underlying MCP server
                    mcp_server = self.server._mcp_server
                    if hasattr(mcp_server, 'request_context') and mcp_server.request_context:
                        if hasattr(mcp_server.request_context, 'session') and mcp_server.request_context.session:
                            session_key = hex(id(mcp_server.request_context.session))
                        else:
                            session_key = "fastmcp_default"
                    else:
                        session_key = "fastmcp_default"
                else:
                    # For low-level MCP servers, access session through request_context
                    if hasattr(self.server, '_mcp_server'):
                        lowlevel_server = self.server._mcp_server
                    else:
                        lowlevel_server = self.server
                    session_key = hex(id(lowlevel_server.request_context.session))

                session_id = self.session_ids.get(session_key)
                if not session_id:
                    session_id = self.start_session(session_key)
                    if not session_id:
                        return False
            except Exception as e:
                logger.warning(f"Failed to get session info: {e}")
                session_id = self.start_session("default_session", return_dummy_session=True)

            # Handle disable_input and disable_output from config
            send_args = args
            send_result = str(result)
            if self.config:
                if self.config.disable_input:
                    send_args = None
                if self.config.disable_output:
                    send_result = None

            response = requests.post(
                f"{self.endpoint}/capture-event",
                headers={
                    "Content-Type": "application/json",
                    "X-Org-Id": self.org_id or "",
                },
                json={
                    "org_id": self.org_id,
                    "session_id": session_id,
                    "primitive_type": primitive_type,
                    "primitive_name": primitive_name,
                    "latency": latency,
                    "success": success,
                    "args": json.dumps(send_args) if send_args is not None else "",
                    "result": json.dumps(send_result) if send_result is not None else "",
                },
                timeout=10
            )
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to record event - API warning: {str(e)}")
            return False
        except Exception as e:
            logger.warning(f"Failed to record event - unexpected warning: {str(e)}")
            return False

    # wip: decorator to wrap functions with analytics. not reachable yet
    def wrap(self, 
             primitive_type: str, 
             primitive_name: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """
        Decorator to wrap a function with analytics tracking. Is in WIP state.

        Args:
            primitive_type: Type of primitive
            primitive_name: Name of the primitive

        Returns:
            Callable: Decorated function with analytics tracking
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> T:
                start_time = time.time()
                success = True
                result = None
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    raise e
                finally:
                    latency = int((time.time() - start_time) * 1000)  # Convert to ms
                    
                    # Combine args and kwargs for analytics
                    all_args = {
                        "args": [str(arg) if not isinstance(arg, (int, float, bool, str, list, dict)) 
                                 else arg for arg in args],
                        "kwargs": {k: v for k, v in kwargs.items() 
                                  if k != "org_id" and isinstance(v, (int, float, bool, str, list, dict))}
                    }
                    
                    try:
                        self.record_event(
                            primitive_type=primitive_type,
                            primitive_name=primitive_name,
                            args=all_args,
                            latency=latency,
                            success=success,
                            result=result
                        )
                    except Exception as e:
                        logger.warning(f"Failed to record analytics: {str(e)}")
            
            return wrapper
        
        return decorator

    def override_fast_mcp_server(self, server: Any) -> bool:
        """
        Monkey-patch FastMCP's ToolManager to intercept tool operations.
        
        Args:
            server: FastMCP server instance
            
        Returns:
            bool: True if patching was successful
        """
        try:
            tool_manager = server._tool_manager
            original_call_tool = tool_manager.call_tool
            if not original_call_tool:
                logger.warning("No call_tool method found")
                return False

            async def patched_call_tool(*args, **kwargs):
                start_time = datetime.now(timezone.utc)
                result = None
                success = True

                # Extract tool name from arguments - FastMCP uses 'key' parameter
                tool_name = kwargs.get('key', kwargs.get('name', 'unknown_tool'))
                arguments = kwargs.get('arguments', {})

                try:
                    result = await original_call_tool(*args, **kwargs)
                    is_error, error_message = is_mcp_error_response(result)
                    if is_error:
                        success = False
                        logger.warning(f"Tool {tool_name} returned error: {error_message}")
                except Exception as e:
                    success = False
                    logger.warning(f"Error calling tool {tool_name}: {str(e)}")
                    raise

                finally:
                    end_time = datetime.now(timezone.utc)
                    latency = int((end_time - start_time).total_seconds() * 1000)
                    self.record_event("tool", str(tool_name), str(arguments), latency, success, result)

                return result

            tool_manager.call_tool = patched_call_tool
            return True
            
        except Exception as e:
            logger.warning(f"Failed to patch FastMCP server: {e}")
            return False

    def override_lowlevel_mcp_server(self, server: Any) -> bool:
        """
        Override low-level MCP server request handlers.
        
        Args:
            server: MCP server instance
            
        Returns:
            bool: True if override was successful
        """
        try:
            original_call_tool_handler = server.request_handlers.get(CallToolRequest)
            if not original_call_tool_handler:
                logger.warning("No CallToolRequest handler found")
                return False

            async def wrapped_call_tool_handler(request: CallToolRequest) -> ServerResult:
                start_time = datetime.now(timezone.utc)
                tool_name = request.params.name
                arguments = request.params.arguments or {}
                result = None
                success = True

                try:
                    result = await original_call_tool_handler(request)
                    is_error, error_message = is_mcp_error_response(result)
                    if is_error:
                        success = False
                        logger.warning(f"Tool {tool_name} returned error: {error_message}")
                except Exception as e:
                    success = False
                    logger.warning(f"Error calling tool {tool_name}: {str(e)}")
                    raise

                finally:
                    end_time = datetime.now(timezone.utc)
                    latency = int((end_time - start_time).total_seconds() * 1000)

                    # Try to get fresh client info during tool execution when context is available
                    try:
                        if hasattr(server, 'request_context') and server.request_context:
                            if hasattr(server.request_context, 'session') and server.request_context.session:
                                fresh_session_key = hex(id(server.request_context.session))
                                if fresh_session_key not in self.session_ids:
                                    # Create a new session with proper client info
                                    client_name = server.request_context.session.client_params.clientInfo.name
                                    self._create_session_with_client_info(fresh_session_key, client_name)
                    except Exception as e:
                        logger.debug(f"Could not refresh session info during tool execution: {e}")

                    self.record_event("tool", str(tool_name), str(arguments), latency, success, result)

                return result

            server.request_handlers[CallToolRequest] = wrapped_call_tool_handler
            return True
            
        except Exception as e:
            logger.warning(f"Failed to override lowlevel MCP server: {e}")
            return False

    def track_mcp(self, server: Any, org_id: str, config: AgnostConfig) -> Any:
        """
        Enable tracking for an MCP server instance.
        
        Args:
            server: MCP server instance to track
            org_id: Organization ID for Agnost Analytics
            config: AgnostConfig instance

        Returns:
            Any: The server instance with tracking enabled
        """
        if not self.initialize(server, org_id, config):
            logger.warning("Failed to initialize analytics")
            return server
            
        try:
            if is_fastmcp_server(server):
                success = self.override_fast_mcp_server(server)
            else:
                success = self.override_lowlevel_mcp_server(server)
    
            if not success:
                logger.warning("Failed to set up MCP tracking")
        except Exception as e:
            logger.warning(f"MCP tracking setup failed: {str(e)}")

        return server
