#!/usr/bin/env python3
"""
Development server script with auto-reload enabled.
Use this for development to automatically restart the server when files change.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."],
        log_level="info"
    )
