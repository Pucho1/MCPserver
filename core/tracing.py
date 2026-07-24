"""
Tracing utilities for instrumenting MCP server operations.

Provides decorators and context managers for automatic trace creation,
span management, and error tracking with Langfuse.

Best practices:
- Use @trace_tool decorator for MCP tool definitions
- Use @trace_service decorator for service methods
- Use trace_operation context manager for any operation
- Always include descriptive names and metadata
"""

import functools
import time
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Callable, Optional, Dict

from core.langfuse_config import langfuse_client
from core.observabiity.null_trace import NullTrace
from core.logger import logger


def _build_metadata(*, tags: Optional[list[str]] = None, **extra: Any) -> Optional[Dict[str, Any]]:
    metadata = dict(extra)
    if tags:
        metadata["tags"] = tags
    return metadata or None


def trace_tool(func: Callable) -> Callable:
    """
    Decorator for tracing MCP tool executions.
    
    Automatically creates a trace for each tool call with:
    - Tool name and execution time
    - Input parameters
    - Output/result data
    - Error tracking
    
    Usage:
        @trace_tool
        async def my_tool(param: str, context: Context) -> dict:
            return {"result": "data"}
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        tool_name = func.__name__
        start_time = time.time()
        
        if not langfuse_client:
            return await func(*args, **kwargs)
        
        try:
            # Extract input from kwargs (exclude context)
            tool_input = {
                k: v for k, v in kwargs.items()
                if k != "context"
            }
            
            # Create a trace for this tool call
            with langfuse_client.start_as_current_observation(
                name=tool_name,
                as_type="tool",
                input=tool_input,
            ) as _:
                result = await func(*args, **kwargs)
                
                # Record successful completion
                duration_ms = round((time.time() - start_time) * 1000, 2)
                langfuse_client.update_current_span(
                    output=result,
                    metadata={
                        "duration_ms": duration_ms,
                        "status": "success"
                    }
                )
                
                return result
                
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Log error to Langfuse
            if langfuse_client:
                langfuse_client.create_event(
                    name=f"{tool_name}-error",
                    input={"error": str(e)},
                    metadata={
                        "duration_ms": duration_ms,
                        "status": "error",
                        "error_type": type(e).__name__
                    },
                    level="ERROR",
                )
            
            logger.error(f"Tool {tool_name} failed: {str(e)}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        tool_name = func.__name__
        start_time = time.time()
        
        if not langfuse_client:
            return func(*args, **kwargs)
        
        try:
            tool_input = {
                k: v for k, v in kwargs.items()
                if k != "context"
            }
            
            with langfuse_client.start_as_current_observation(
                name=tool_name,
                as_type="tool",
                input=tool_input,
            ) as _:
                result = func(*args, **kwargs)
                
                duration_ms = round((time.time() - start_time) * 1000, 2)
                langfuse_client.update_current_span(
                    output=result,
                    metadata={
                        "duration_ms": duration_ms,
                        "status": "success"
                    }
                )
                
                return result
                
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            if langfuse_client:
                langfuse_client.create_event(
                    name=f"{tool_name}-error",
                    input={"error": str(e)},
                    metadata={
                        "duration_ms": duration_ms,
                        "status": "error",
                        "error_type": type(e).__name__
                    },
                    level="ERROR",
                )
            
            logger.error(f"Tool {tool_name} failed: {str(e)}")
            raise
    
    # Return appropriate wrapper
    if hasattr(func, "__await__"):
        return async_wrapper
    else:
        # Check if function is coroutine function
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper


def trace_service(func: Callable) -> Callable:
    """
    Decorator for tracing service method executions.
    
    Creates a span for service operations with:
    - Method name
    - Execution time
    - Result/Error tracking
    
    Usage:
        class NotesService:
            @trace_service
            async def create_note(self, content: str):
                return note_id
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        method_name = func.__name__
        class_name = args[0].__class__.__name__ if args else "unknown"
        span_name = f"{class_name}.{method_name}"
        
        if not langfuse_client:
            return await func(*args, **kwargs)
        
        start_time = time.time()
        
        try:
            with langfuse_client.start_as_current_observation(
                name=span_name,
                as_type="span",
                input={"args": str(args[1:]), "kwargs": str(kwargs)},
            ) as _:
                result = await func(*args, **kwargs)
                
                duration_ms = round((time.time() - start_time) * 1000, 2)
                langfuse_client.update_current_span(
                    output=str(result),
                    metadata={
                        "duration_ms": duration_ms,
                        "status": "success"
                    }
                )
                
                return result
                
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            if langfuse_client:
                langfuse_client.create_event(
                    name=f"{span_name}-error",
                    input={"error": str(e)},
                    metadata={
                        "duration_ms": duration_ms,
                        "status": "error",
                        "error_type": type(e).__name__
                    },
                    level="ERROR",
                )
            
            logger.error(f"Service method {span_name} failed: {str(e)}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        method_name = func.__name__
        class_name = args[0].__class__.__name__ if args else "unknown"
        span_name = f"{class_name}.{method_name}"
        
        if not langfuse_client:
            return func(*args, **kwargs)
        
        start_time = time.time()
        
        try:
            with langfuse_client.start_as_current_observation(
                name=span_name,
                as_type="span",
                input={"args": str(args[1:]), "kwargs": str(kwargs)},
            ) as _:
                result = func(*args, **kwargs)
                
                duration_ms = round((time.time() - start_time) * 1000, 2)
                langfuse_client.update_current_span(
                    output=str(result),
                    metadata={
                        "duration_ms": duration_ms,
                        "status": "success"
                    }
                )
                
                return result
                
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            if langfuse_client:
                langfuse_client.create_event(
                    name=f"{span_name}-error",
                    input={"error": str(e)},
                    metadata={
                        "duration_ms": duration_ms,
                        "status": "error",
                        "error_type": type(e).__name__
                    },
                    level="ERROR",
                )
            
            logger.error(f"Service method {span_name} failed: {str(e)}")
            raise
    
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


@asynccontextmanager
async def trace_operation(
    name: str,
    input_data: Optional[Dict[str, Any]] = None,
    tags: Optional[list[str]] = None,
):
    """
    Context manager for tracing any operation.
    
    Creates a span around a code block with automatic
    timing and error tracking.
    
    Usage:
        async with trace_operation("process_request", input_data={"user": "123"}):
            await process()
    """
    if not langfuse_client:
        yield NullTrace()
        return
    
    start_time = time.time()
    
    try:
        with langfuse_client.start_as_current_observation(
            name=name,
            as_type="span",
            input=input_data,
            metadata=_build_metadata(tags=tags),
        ) as span:
            yield span
            
            duration_ms = round((time.time() - start_time) * 1000, 2)
            langfuse_client.update_current_span(
                metadata={
                    "duration_ms": duration_ms,
                    "status": "success"
                }
            )
            
    except Exception as e:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        if langfuse_client:
            langfuse_client.create_event(
                name=f"{name}-error",
                input={"error": str(e)},
                metadata={
                    "duration_ms": duration_ms,
                    "status": "error",
                    "error_type": type(e).__name__
                },
                level="ERROR",
            )
        
        logger.error(f"Operation {name} failed: {str(e)}")
        raise


@contextmanager
def trace_operation_sync(
    name: str,
    input_data: Optional[Dict[str, Any]] = None,
    tags: Optional[list[str]] = None,
):
    """
    Synchronous context manager for tracing operations.
    
    Usage:
        with trace_operation_sync("read_file", input_data={"path": "/path"}):
            content = read_file()
    """
    if not langfuse_client:
        yield NullTrace()
        return
    
    start_time = time.time()
    
    try:
        with langfuse_client.start_as_current_observation(
            name=name,
            as_type="span",
            input=input_data,
            metadata=_build_metadata(tags=tags),
        ) as span:
            yield span
            
            duration_ms = round((time.time() - start_time) * 1000, 2)
            langfuse_client.update_current_span(
                metadata={
                    "duration_ms": duration_ms,
                    "status": "success"
                }
            )
            
    except Exception as e:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        if langfuse_client:
            langfuse_client.create_event(
                name=f"{name}-error",
                input={"error": str(e)},
                metadata={
                    "duration_ms": duration_ms,
                    "status": "error",
                    "error_type": type(e).__name__
                },
                level="ERROR",
            )
        
        logger.error(f"Operation {name} failed: {str(e)}")
        raise


def trace_event(
    name: str,
    input_data: Optional[Dict[str, Any]] = None,
    tags: Optional[list[str]] = None,
):
    """
    Log a point-in-time event to Langfuse.
    
    Useful for marking important moments without duration.
    
    Usage:
        trace_event("user_authenticated", {"user_id": "123"}, tags=["auth"])
    """
    if not langfuse_client:
        return
    
    try:
        langfuse_client.create_event(
            name=name,
            input=input_data,
            metadata=_build_metadata(tags=tags),
        )
    except Exception as e:
        logger.error(f"Failed to record event {name}: {str(e)}")
