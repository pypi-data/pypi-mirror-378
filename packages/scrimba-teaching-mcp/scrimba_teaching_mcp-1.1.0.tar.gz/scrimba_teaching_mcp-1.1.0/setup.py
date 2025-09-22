#!/usr/bin/env python3
"""
Setup script for Scrimba Teaching MCP System
"""

from setuptools import setup, find_packages

setup(
    name="scrimba-teaching-mcp",
    version="1.0.0",
    description="Scrimba-style teaching system for Claude Desktop and CLI",
    author="Scrimba Teaching System",
    packages=find_packages(),
    install_requires=[
        "fastmcp>=0.1.0",
        "starlette",
        "uvicorn"
    ],
    entry_points={
        "console_scripts": [
            "scrimba-teaching-server=teaching_server.teaching_mcp:main",
            "claude-cli-wrapper=cli_wrapper.cli_wrapper_mcp:main",
        ],
    },
    python_requires=">=3.8",
)