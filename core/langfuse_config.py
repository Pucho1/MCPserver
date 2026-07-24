"""
Langfuse configuration and setup for MCP server tracing.

This module initializes the Langfuse client and provides utilities
for instrumenting the MCP server with observability tracing.
"""

import os
from langfuse import Langfuse
from core.logger import logger
from config.settings import load_settings



def get_langfuse_client() -> Langfuse:
    """
    Initialize and return the Langfuse client.
    
    The client is a singleton that uses environment variables:
    - LANGFUSE_PUBLIC_KEY
    - LANGFUSE_SECRET_KEY
    - LANGFUSE_BASE_URL (optional, defaults to https://cloud.langfuse.com)
    
    Returns:
        Langfuse: Configured Langfuse client instance
    """
    try:
        settings = load_settings()
        public_key = settings.LANGFUSE_PUBLIC_KEY
        secret_key = settings.LANGFUSE_SECRET_KEY
        base_url = settings.LANGFUSE_BASE_URL
        
        if not public_key or not secret_key:
            logger.warning(
                "Langfuse credentials not found. Tracing will be disabled. "
                "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY to enable."
            )
            return None
        
        langfuse = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            base_url=base_url,
            debug=False,
            flush_interval=1.0,  # Flush events every 1 second
        )
        
        # Verify connection
        if langfuse.auth_check():
            logger.info("✓ Langfuse client authenticated successfully")
            return langfuse
        else:
            logger.warning(
                "Langfuse authentication check failed. "
                "Please verify your credentials."
            )
            return None
            
    except Exception as e:
        logger.error(f"Failed to initialize Langfuse: {str(e)}")
        return None


# Initialize singleton client
langfuse_client = get_langfuse_client()
