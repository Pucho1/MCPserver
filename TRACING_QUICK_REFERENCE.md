# Langfuse Tracing Quick Reference

## For Developers

### Import Statements

```python
# Decorators for tools and services
from core.tracing import trace_tool, trace_service

# Context managers for operations
from core.tracing import trace_operation, trace_operation_sync

# Point-in-time events
from core.tracing import trace_event

# Direct client access (if needed)
from core.langfuse_config import langfuse_client
```

## Common Patterns

### Pattern 1: Trace a New MCP Tool

```python
from fastmcp import Context
from core.mcp_instance import mcp
from core.tracing import trace_tool

@mcp.tool()
@trace_tool
async def my_tool(param: str, context: Context) -> str:
    """Tool description."""
    # Your implementation
    return "result"
```

**Result**: Automatically traced tool call with input, output, timing, and errors.

### Pattern 2: Trace a Service Method

```python
from core.tracing import trace_service

class MyService:
    @trace_service
    async def create_item(self, data: str) -> int:
        """Create an item."""
        # Your implementation
        return item_id
```

**Result**: Service method execution is traced as a span within tool traces.

### Pattern 3: Trace a Complex Operation

```python
from core.tracing import trace_operation

@mcp.tool()
@trace_tool
async def complex_tool(param: str, context: Context) -> dict:
    """Complex multi-step operation."""
    
    # Step 1: Parse
    async with trace_operation(
        "parse_input",
        input_data={"param_size": len(param)},
        tags=["parsing"]
    ):
        parsed = parse(param)
    
    # Step 2: Validate
    async with trace_operation(
        "validate_data",
        input_data={"items": len(parsed)},
        tags=["validation"]
    ):
        valid = validate(parsed)
    
    # Step 3: Process
    async with trace_operation(
        "process_data",
        tags=["processing"]
    ) as span:
        result = await process(valid)
        span.update(output={"status": "processed"})
    
    return result
```

**Result**: Three nested spans showing the operation flow.

### Pattern 4: Trace a Synchronous Operation

```python
from core.tracing import trace_operation_sync

def my_sync_function():
    with trace_operation_sync(
        "sync_operation",
        input_data={"config": "value"},
        tags=["sync"]
    ):
        # Your synchronous code
        result = do_something()
    
    return result
```

**Result**: Synchronous operation traced without async context.

### Pattern 5: Log a Point-in-Time Event

```python
from core.tracing import trace_event

@mcp.tool()
@trace_tool
async def my_tool(param: str, context: Context) -> str:
    # Some operation...
    
    trace_event(
        name="important_milestone",
        input_data={"user": "123", "action": "completed"},
        tags=["milestone", "important"]
    )
    
    # Continue...
    return "done"
```

**Result**: Event appears in Langfuse timeline.

### Pattern 6: Add Custom Metadata to a Span

```python
from core.langfuse_config import langfuse_client

@trace_service
async def method_with_metadata(self):
    if langfuse_client:
        with langfuse_client.span("operation") as span:
            result = await self.do_work()
            
            # Add custom metadata
            span.update(
                metadata={
                    "environment": "production",
                    "database": "postgresql",
                    "cache_hit": True,
                }
            )
    
    return result
```

**Result**: Custom metadata visible in Langfuse dashboard.

### Pattern 7: Access Current Span

```python
from core.langfuse_config import langfuse_client

@trace_operation
async def operation():
    # If you need to access the current span
    if langfuse_client:
        # Get current span via context (OpenTelemetry-based)
        pass
```

## Naming Conventions

### Tool Names
- Use lowercase with underscores: `create_note`, `get_user_profile`
- Same as the function name: `create_note()` function → `"create_note"` trace

### Operation Names
- Verb + noun: `"parse_json"`, `"validate_request"`, `"fetch_data"`
- Use snake_case: `"process_batch"`, `"save_to_database"`

### Tags
- Use lowercase: `"parsing"`, `"validation"`, `"database"`
- Specific and descriptive: `"tool-call"`, `"error-handling"`, `"startup"`

## Performance Tips

### ✅ DO

```python
# ✅ Good: Minimal input data
async with trace_operation("process", input_data={"id": 123}):
    await process()

# ✅ Good: Use tags for filtering
trace_event("processed", tags=["batch", "important"])

# ✅ Good: Explicit operation boundaries
@trace_service
async def method(self):
    return await db.query()
```

### ❌ DON'T

```python
# ❌ Bad: Large input data
async with trace_operation("process", input_data={"entire_database": huge_dict}):
    pass

# ❌ Bad: No tags for organization
trace_event("something_happened")

# ❌ Bad: Manual span management (use decorators instead)
from langfuse import get_client
langfuse = get_client()
with langfuse.span("operation"):
    # This is allowed but decorators are simpler
    pass
```

## Testing with Tracing

### Disable Tracing in Tests

```python
# In your test setup
import os
os.environ["LANGFUSE_PUBLIC_KEY"] = ""
os.environ["LANGFUSE_SECRET_KEY"] = ""

# or

# In tests, if langfuse_client is None, tracing is gracefully disabled
from core.langfuse_config import langfuse_client

def test_something():
    # Tracing will be skipped if langfuse_client is None
    # Tests run normally
    pass
```

## Debugging Tips

### Check if Langfuse is Connected

```python
from core.langfuse_config import langfuse_client

if langfuse_client is None:
    print("Langfuse tracing is disabled")
else:
    print("Langfuse is connected and tracing is active")
```

### View Logs

```bash
# Trace logs appear in your application logs
# Look for messages like:
# "✓ Langfuse client authenticated successfully"
# "Failed to record event operation_name: ..."
```

### Manual Flush

```python
from core.langfuse_config import langfuse_client

# Ensure all traces are sent
if langfuse_client:
    langfuse_client.flush()

# Shutdown gracefully
if langfuse_client:
    langfuse_client.shutdown()
```

## Common Issues

### Issue: No traces appear

**Solution**: 
1. Check credentials in `.env`
2. Verify network connectivity
3. Check logs for authentication errors
4. Manually call `langfuse_client.flush()`

### Issue: Too many traces

**Solution**:
1. Use tags to organize traces
2. Filter in Langfuse UI by session or tags
3. Consider trace sampling for high-volume operations

### Issue: Long trace names

**Solution**:
Use shorter, more descriptive names:
- ✅ `"parse"` instead of ❌ `"parse_json_input_string_with_validation"`

## Next Steps

1. **Review** [LANGFUSE_INTEGRATION.md](LANGFUSE_INTEGRATION.md) for full documentation
2. **Explore** traces in [Langfuse Cloud](https://cloud.langfuse.com/)
3. **Add** custom tracing to your business logic
4. **Monitor** performance and error trends over time

## File Reference

- `core/langfuse_config.py` — Client initialization
- `core/tracing.py` — Decorators and utilities (start here!)
- `core/lifespan.py` — Server lifecycle tracing
- `middleware/debug.py` — Middleware integration
- `LANGFUSE_INTEGRATION.md` — Full documentation

---

**Questions?** Check [Langfuse Docs](https://langfuse.com/docs) or the [Python SDK Reference](https://python.reference.langfuse.com)
