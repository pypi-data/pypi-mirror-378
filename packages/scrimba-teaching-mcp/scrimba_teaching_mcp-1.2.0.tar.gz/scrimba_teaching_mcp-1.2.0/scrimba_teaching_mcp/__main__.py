#!/usr/bin/env python3
"""
Main entry point for Scrimba Teaching MCP Server
"""

from .teaching_server import mcp

def main():
    """Run the MCP server."""
    print("Starting Scrimba Teaching MCP Server...")
    print("Ready to teach with revolutionary methodology!")
    print("=" * 60)
    mcp.run()

if __name__ == "__main__":
    main()