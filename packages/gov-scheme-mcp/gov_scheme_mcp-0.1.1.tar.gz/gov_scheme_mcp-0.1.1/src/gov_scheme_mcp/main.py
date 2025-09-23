#!/usr/bin/env python3
"""Main entry point for the Government Scheme MCP server."""

import sys
from .server import run_server

def main():
    """Main entry point for the CLI."""
    try:
        run_server()
    except KeyboardInterrupt:
        print("\nServer stopped.", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()