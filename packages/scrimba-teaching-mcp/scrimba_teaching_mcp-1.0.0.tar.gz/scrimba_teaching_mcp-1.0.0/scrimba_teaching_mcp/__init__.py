"""
Scrimba Teaching MCP - Interactive programming teacher using Scrimba's methodology
"""

__version__ = "1.0.0"
__author__ = "Scrimba Teaching System"

from .teaching_server import (
    teach,
    give_challenge, 
    check_code,
    next_lesson,
    start_project,
    visualize_concept,
    show_progress
)

__all__ = [
    "teach",
    "give_challenge",
    "check_code", 
    "next_lesson",
    "start_project",
    "visualize_concept",
    "show_progress"
]