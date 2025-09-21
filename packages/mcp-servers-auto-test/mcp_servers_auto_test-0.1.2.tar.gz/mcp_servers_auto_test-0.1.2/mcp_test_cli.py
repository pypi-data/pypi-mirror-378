#!/usr/bin/env python3
"""
MCP Test Command Line Interface
This file serves as the entry point for the 'mcp-test' command.
"""

import asyncio
import sys
from main import main

def cli_main():
    """CLI entry point that handles the mcp-test command"""
    try:
        # Run the async main function
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nMCP Test application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli_main()
