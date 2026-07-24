# Getting Started with Langfuse Tracing

## ⚡ Quick Start (5 minutes)

### 1. Prerequisites
- ✅ Langfuse SDK is installed (`langfuse==4.14.0`)
- ✅ Tracing code is integrated throughout the application
- ✅ `.env` file contains Langfuse credentials

### 2. Verify Installation

```bash
# Run verification script
python verify_langfuse.py
```

Expected output:
```
✓ All modules with tracing loaded successfully
✓ Langfuse integration verification completed!
```

### 3. Start the Server

```bash
# Start MCP server with tracing enabled
uv run server.py
```

### 4. Generate Some Traces

In another terminal:
```bash
# Run client to call tools
uv run client.py
```

### 5. View Traces

1. Open [Langfuse Cloud](https://cloud.langfuse.com/)
2. Login with your credentials
3. Select your project
4. You should see traces for the "mcp-server" session

---

## 📚 Documentation Files

### For Setup
- **[README.md](README.md)** — Project overview and setup instructions
- **[LANGFUSE_INTEGRATION.md](LANGFUSE_INTEGRATION.md)** — Complete integration guide

### For Developers
- **[TRACING_QUICK_REFERENCE.md](TRACING_QUICK_REFERENCE.md)** — Code examples and patterns
- **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** — What was implemented

### For Testing
- **[verify_langfuse.py](verify_langfuse.py)** — Verify integration is working

---

## 🔍 Understanding What's Traced

### Every MCP Tool Call
When you call any tool, a trace is automatically created with:
- Input parameters
- Output result
- Execution time
- Any errors that occur

### Example: Create a Note
```bash
# Client calls the tool
await session.call_tool("create_note", arguments={"content": "Hello"})
```

In Langfuse, you'll see:
```
Trace: create_note
├── Input: {"content": "Hello"}
├── Service Call: NotesService.create_note
│   ├── Database Insert
│   └── Timing: 38ms
├── Output: "Nota creada con id 1"
└── Total Time: 45ms
```

---

## 💡 Common Tasks

### View All Traces for Your Server
1. Go to [Langfuse Cloud](https://cloud.langfuse.com/)
2. Select your project
3. Filter by Session: "mcp-server"
4. All traces for your server are here

### Find Slow Operations
1. Go to Traces view
2. Sort by "Duration" (descending)
3. Identify bottlenecks

### Find Errors
1. Go to Traces view
2. Filter by Status: "Error"
3. See which tools are failing

### Add Custom Tracing to Your Code
See [TRACING_QUICK_REFERENCE.md](TRACING_QUICK_REFERENCE.md) for examples

---

## 🚀 Next Steps

### Level 1: Basic (You are here)
- ✅ Understand what's traced
- ✅ View traces in Langfuse dashboard
- Next: Monitor performance

### Level 2: Monitoring
- 📊 Create dashboards for your metrics
- 📈 Track error rates and latency
- ⏰ Set up alerts for anomalies
- Next: Add custom tracing

### Level 3: Advanced
- 🎯 Add custom tracing to business logic
- 🏷️ Tag traces for better filtering
- 📝 Use traces for debugging
- 🔗 Correlate with external systems
- Next: Use for optimization

### Level 4: Production
- 🛡️ Monitor production traces continuously
- 📊 Create dashboards for stakeholders
- 🎓 Use tracing for troubleshooting
- 🚀 Optimize based on trace data

---

## 🛠️ Troubleshooting

### Problem: No traces appear in Langfuse

**Solution:**
1. Verify credentials are correct
   ```bash
   # Check .env file
   echo $LANGFUSE_PUBLIC_KEY
   echo $LANGFUSE_SECRET_KEY
   ```

2. Check server logs for authentication messages
   ```bash
   # Should see: "✓ Langfuse client authenticated successfully"
   ```

3. Verify network connectivity
   ```bash
   # Can you reach Langfuse?
   curl https://cloud.langfuse.com
   ```

### Problem: Too many traces

**Solution:**
- Use tags to organize: `tags=["important"]`
- Filter in dashboard
- Check Langfuse retention settings

### Problem: High application latency

**Solution:**
- Tracing is non-blocking (async)
- Verify not a network issue to Langfuse
- Check Langfuse `flush_interval` setting

---

## 📖 Code Examples

### Example 1: Calling a Traced Tool
```python
from mcp.client.session import ClientSession

async with ClientSession(...) as session:
    # This tool call is automatically traced
    result = await session.call_tool(
        "create_note",
        arguments={"content": "My note"}
    )
    # In Langfuse, you'll see a trace for this call
```

### Example 2: Adding Custom Tracing
```python
from core.tracing import trace_operation

@mcp.tool()
async def process_data(data: str, context: Context) -> dict:
    # Custom span for specific operation
    async with trace_operation(
        "parse_input",
        input_data={"size": len(data)}
    ):
        parsed = json.loads(data)
    
    return {"items": len(parsed)}
```

### Example 3: Tracing a Complex Operation
```python
from core.tracing import trace_operation

async def complex_workflow():
    # Step 1: Parse
    async with trace_operation("step1_parse"):
        data = parse_input()
    
    # Step 2: Validate
    async with trace_operation("step2_validate"):
        validated = validate(data)
    
    # Step 3: Process
    async with trace_operation("step3_process"):
        result = await process(validated)
    
    return result
```

---

## 📞 Support

### Getting Help

1. **Quick Questions**: Check [TRACING_QUICK_REFERENCE.md](TRACING_QUICK_REFERENCE.md)
2. **Setup Issues**: See [LANGFUSE_INTEGRATION.md](LANGFUSE_INTEGRATION.md)
3. **Langfuse Docs**: https://langfuse.com/docs
4. **Python SDK**: https://python.reference.langfuse.com

### Reporting Issues

If tracing isn't working:
1. Run `python verify_langfuse.py`
2. Check server logs for errors
3. Verify `.env` credentials
4. Check [LANGFUSE_INTEGRATION.md](LANGFUSE_INTEGRATION.md#troubleshooting)

---

## 🎯 Key Points to Remember

1. **Automatic**: All MCP tools are automatically traced
2. **Non-blocking**: Tracing won't slow down your application
3. **Graceful**: If credentials missing, tracing silently disables
4. **Extensible**: Easy to add custom tracing with decorators
5. **Organized**: All traces grouped under "mcp-server" session

---

## 📊 Dashboard Tips

### Useful Filters
- **Session**: Filter by "mcp-server" to see only your server traces
- **Tags**: Filter by operation type (tool-call, parsing, database, etc.)
- **Status**: Filter by success/error
- **Duration**: Find slow operations
- **Tool**: Filter by specific tool name

### Dashboard Actions
- Click trace to see details
- Click span to see timing breakdown
- Filter to find patterns
- Create alerts for errors
- Export data for analysis

---

## ✅ Verification Checklist

Before running in production:

- [ ] Ran `python verify_langfuse.py` successfully
- [ ] Can view traces in Langfuse dashboard
- [ ] Tool calls appear in traces
- [ ] Service methods appear as nested spans
- [ ] Errors are captured correctly
- [ ] Read [LANGFUSE_INTEGRATION.md](LANGFUSE_INTEGRATION.md)
- [ ] Reviewed [TRACING_QUICK_REFERENCE.md](TRACING_QUICK_REFERENCE.md)
- [ ] Understood architecture in [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)

---

## 🚀 You're Ready!

Your MCP server now has enterprise-grade distributed tracing. 

**Next**: Start the server and begin monitoring your traces in Langfuse!

```bash
# Start server
uv run server.py

# Open dashboard
# https://cloud.langfuse.com/project/your-project
```

Happy tracing! 🎉
