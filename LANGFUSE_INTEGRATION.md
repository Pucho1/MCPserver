# Langfuse Integration Guide

This document explains how Langfuse tracing has been integrated into your MCP server following best practices.

## Overview

Your MCP server now includes comprehensive distributed tracing via Langfuse. This enables:

- **Full request tracing**: Track every MCP tool call from start to finish
- **Performance monitoring**: Automatic latency measurements for all operations
- **Error tracking**: Detailed error logs with context and timing
- **Service-level observability**: Trace database operations, API calls, and more
- **Middleware integration**: Automatic span creation at the MCP protocol level

## Setup

### 1. Environment Configuration

Your `.env` file already contains Langfuse credentials:

```bash
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_BASE_URL="https://cloud.langfuse.com"
```

To use your own Langfuse instance:
- Sign up at [Langfuse Cloud](https://cloud.langfuse.com/) (or self-host)
- Navigate to Settings → API Keys
- Copy your `PUBLIC_KEY` and `SECRET_KEY`
- Update the `.env` file with your credentials
- For self-hosted instances, update `LANGFUSE_BASE_URL`

### 2. Installation

The Langfuse SDK is already added to `pyproject.toml`:

```bash
uv sync
```

## Architecture

### Component Hierarchy

```
Langfuse Client (core/langfuse_config.py)
    ↓
Tracing Utilities (core/tracing.py)
    ├── @trace_tool (for MCP tools)
    ├── @trace_service (for service methods)
    ├── trace_operation (async context manager)
    └── trace_event (point-in-time logging)
    ↓
Middleware Layer (middleware/debug.py)
    ├── DebugMiddleware (logs + Langfuse spans)
    ├── AuthMiddleware (event logging)
    └── RateLimitMiddleware (optional)
    ↓
Tools & Services
    ├── Notes Service (traced methods)
    ├── REST Service (traced methods)
    ├── Health Service (traced methods)
    └── Filesystem Service (traced operations)
    ↓
Lifespan Management (core/lifespan.py)
    └── Server startup/shutdown events
```

### Tracing Layers

1. **Middleware Layer**: Captures every MCP tool invocation with timing and errors
2. **Service Layer**: Traces individual database and API operations
3. **Tool Layer**: Explicit tracing at the MCP protocol level
4. **Lifespan Layer**: Traces server startup and shutdown events

## Best Practices Implemented

### 1. Decorators for Automatic Tracing

```python
from core.tracing import trace_tool, trace_service

# For MCP tools
@mcp.tool()
@trace_tool
async def my_tool(param: str, context: Context) -> str:
    return await service.process(param)

# For service methods
class MyService:
    @trace_service
    async def create_item(self, data: str):
        return await db.insert(data)
```

**Benefits**:
- Minimal code changes required
- Consistent tracing across all tools
- Automatic timing and error tracking
- No need to manage span lifecycle manually

### 2. Context Managers for Operations

```python
from core.tracing import trace_operation

async with trace_operation(
    "process_batch",
    input_data={"batch_id": "123"},
    tags=["batch-processing"]
):
    # Your code here
    await process()
```

**When to use**:
- Complex multi-step operations
- Database transactions
- Long-running tasks
- When you need to associate data with a span

### 3. Middleware Integration

The `DebugMiddleware` automatically:
- Creates spans for each tool call
- Measures execution time
- Tracks errors with stack traces
- Generates unique request IDs
- Integrates with existing logging

**No additional code needed** — all tool calls are automatically traced.

### 4. Session and User Tracking

All traces are grouped under a session:

```python
# All traces in your MCP server use "mcp-server" as session_id
langfuse_client.span(
    name="operation",
    input={"data": "..."},
    tags=["tag1", "tag2"],
)
```

To add user-level tracking in your tools:

```python
@mcp.tool()
@trace_tool
async def my_tool(user_id: str, context: Context) -> dict:
    # Optionally add user tracking
    from core.langfuse_config import langfuse_client
    if langfuse_client:
        # Langfuse will track this user across traces
        pass
    return {}
```

### 5. Error Handling and Observability

Errors are automatically captured with:
- Error message
- Error type
- Duration before error occurred
- Request ID for correlation

```python
@trace_service
async def risky_operation(self):
    # If this raises an exception, it's automatically
    # traced with error context
    await db.risky_query()
```

## Current Instrumentation

### Tools Traced
- ✅ `create_note`
- ✅ `get_single_note`
- ✅ `get_list_notes`
- ✅ `update_note`
- ✅ `delete_note`
- ✅ `get_post`
- ✅ `health_check`

### Services Traced
- ✅ `NotesService` (all methods)
- ✅ `PostService.get_post()`
- ✅ `HealthService.check()`

### Middleware
- ✅ `DebugMiddleware` (tool-level tracing)
- ✅ `AuthMiddleware` (authentication events)

### Server Lifecycle
- ✅ Server startup (`mcp_server_startup`)
- ✅ Server shutdown (`mcp_server_shutdown`)

## Usage Examples

### Example 1: Viewing a Tool Trace

When you run a tool:
```python
# Tool call
await session.call_tool("create_note", arguments={"content": "Hello"})
```

In Langfuse dashboard, you'll see:
```
Trace: create_note
├── Input: {"content": "Hello"}
├── Duration: 45ms
├── Output: "Nota creada con id 1"
└── Metadata:
    ├── status: "success"
    └── request_id: "550e8400-e29b-41d4-a716-446655440000"
```

### Example 2: Viewing a Service Trace

Each service method appears as a nested span:
```
Trace: create_note
├── Span: NotesService.create_note
│   ├── Duration: 38ms
│   ├── Input: {"args": "(1,)", "kwargs": "{}"}
│   └── Output: "1"
└── Metadata: {status: "success"}
```

### Example 3: Adding Custom Tracing

In a tool implementation:

```python
@mcp.tool()
@trace_tool
async def process_data(data: str, context: Context) -> dict:
    from core.tracing import trace_operation
    
    # Trace a specific operation
    async with trace_operation(
        "parse_json",
        input_data={"data_size": len(data)},
        tags=["parsing"]
    ) as span:
        parsed = json.loads(data)
        span.update(output={"parsed_items": len(parsed)})
    
    # Continue processing
    return await service.process(parsed)
```

## Accessing Traces in Langfuse

1. **Dashboard**: https://cloud.langfuse.com/project/your-project
2. **Filter by session**: "mcp-server" session ID
3. **Search by tags**: "tool-call", "startup", "shutdown"
4. **Timeline view**: See execution order and timing
5. **Error tracking**: Filter to error status traces

## Performance Considerations

Langfuse is designed for minimal overhead:

- **Async by default**: Events are batched and sent asynchronously
- **Configurable flush**: `flush_interval=1.0` (1 second)
- **No request blocking**: Your tools won't wait for tracing to complete
- **Fault tolerant**: Errors in tracing won't break your application

### Configuration

In `core/langfuse_config.py`:

```python
langfuse = Langfuse(
    public_key=public_key,
    secret_key=secret_key,
    base_url=base_url,
    debug=False,                    # Disable debug logging in production
    flush_interval=1.0,             # Flush every 1 second
)
```

## Troubleshooting

### No traces appearing in Langfuse

1. **Check credentials**: Verify `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY`
2. **Check logs**: Look for "Langfuse client authenticated successfully"
3. **Check network**: Ensure outbound HTTPS to `cloud.langfuse.com` (or your self-hosted instance)
4. **Flush manually**: Add `langfuse_client.flush()` before server shutdown

### Too many traces

- Use `tags` to organize traces
- Filter by session: "mcp-server"
- Use Langfuse's retention settings in project settings

### High latency

- Langfuse is non-blocking, latency impact is minimal (<1ms)
- Check network latency to Langfuse cloud
- Verify background thread is not saturated

## Adding More Tracing

### Trace a new tool

```python
from core.tracing import trace_tool

@mcp.tool()
@trace_tool
async def new_tool(param: str, context: Context) -> str:
    """Your tool description."""
    return "result"
```

### Trace a new service method

```python
from core.tracing import trace_service

class MyService:
    @trace_service
    async def my_method(self, input_data: str) -> dict:
        return {"result": "data"}
```

### Trace an operation

```python
from core.tracing import trace_operation

@mcp.tool()
async def my_tool(param: str, context: Context) -> str:
    async with trace_operation(
        "operation_name",
        input_data={"param": param},
        tags=["tag1", "tag2"]
    ):
        # Your code
        return "result"
```

## Advanced Features

### Custom Attributes

Add custom metadata to any span:

```python
@trace_service
async def method(self):
    from core.langfuse_config import langfuse_client
    
    with langfuse_client.span("operation") as span:
        span.update(
            metadata={
                "custom_field": "custom_value",
                "database": "postgresql",
            }
        )
```

### Scoring (Evaluation)

Add quality scores to traces:

```python
from core.langfuse_config import langfuse_client

langfuse_client.score(
    trace_id="trace-id",
    name="quality",
    value=0.95,
)
```

## Related Files

- [core/langfuse_config.py](../core/langfuse_config.py) — Langfuse client initialization
- [core/tracing.py](../core/tracing.py) — Tracing decorators and utilities
- [core/lifespan.py](../core/lifespan.py) — Server lifecycle tracing
- [middleware/debug.py](../middleware/debug.py) — Middleware integration

## References

- [Langfuse Documentation](https://langfuse.com/docs)
- [Python SDK Reference](https://python.reference.langfuse.com)
- [Best Practices](https://langfuse.com/docs/observability/overview)
- [Troubleshooting](https://langfuse.com/docs/observability/sdk/troubleshooting-and-faq)

## Summary

Your MCP server now has production-grade tracing with:

✅ Automatic tool-level tracing  
✅ Service method instrumentation  
✅ Middleware integration  
✅ Error tracking and reporting  
✅ Performance monitoring  
✅ Session and request correlation  
✅ Minimal performance overhead  
✅ Easy to extend with custom tracing  

All tracing follows Langfuse best practices and integrates seamlessly with your existing FastMCP architecture.
