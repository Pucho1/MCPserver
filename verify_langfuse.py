#!/usr/bin/env python
"""Quick verification that Langfuse integration is working."""

import sys
import os

# Add project to path
sys.path.insert(0, os.getcwd())

print("=" * 60)
print("Langfuse Integration Verification")
print("=" * 60)

try:
    print("\n[1/3] Loading Langfuse configuration...")
    from core.langfuse_config import langfuse_client
    if langfuse_client:
        print("✓ Langfuse client initialized successfully")
        print(f"  Base URL: {langfuse_client.base_url}")
    else:
        print("⚠ Langfuse client not initialized (credentials missing)")
except Exception as e:
    print(f"✗ Failed to load Langfuse config: {e}")
    sys.exit(1)

try:
    print("\n[2/3] Loading tracing utilities...")
    from core.tracing import trace_tool, trace_service, trace_operation, trace_event
    print("✓ Tracing decorators loaded successfully")
    print("  - @trace_tool")
    print("  - @trace_service")
    print("  - trace_operation (async context manager)")
    print("  - trace_event (point-in-time logging)")
except Exception as e:
    print(f"✗ Failed to load tracing utilities: {e}")
    sys.exit(1)

try:
    print("\n[3/3] Verifying modules with tracing...")
    from tools.notes import create_note
    from services.notes_service import NotesService
    from middleware.debug import DebugMiddleware
    print("✓ All modules with tracing loaded successfully")
    print("  - tools/notes.py (traced)")
    print("  - services/notes_service.py (traced)")
    print("  - middleware/debug.py (traced)")
except Exception as e:
    print(f"✗ Failed to load traced modules: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ Langfuse integration verification completed!")
print("=" * 60)
print("\nNext steps:")
print("1. Start the server: uv run server.py")
print("2. Run a tool to generate traces")
print("3. View traces at: https://cloud.langfuse.com/project/your-project")
print("\nDocumentation:")
print("- Full guide: LANGFUSE_INTEGRATION.md")
print("- Quick reference: TRACING_QUICK_REFERENCE.md")
print("=" * 60)
