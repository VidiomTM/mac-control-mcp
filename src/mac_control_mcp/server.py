"""MCP server: registers all mac-control tools via FastMCP."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mac_control_mcp.tools.apple_tools import register_apple_tools
from mac_control_mcp.tools.ax_tools import register_ax_tools
from mac_control_mcp.tools.osa_tools import register_osa_tools
from mac_control_mcp.tools.vision_tools import register_vision_tools


def create_server() -> FastMCP:
    mcp = FastMCP(
        "mac-control",
        instructions=(
            "macOS gap-filler for cua-driver: raw AX snapshot (Catalyst/non-AX apps), "
            "screen capture + on-device OCR, Spotlight/mdfind, and AppleScript/JXA + "
            "Apple apps (Mail, Calendar, Reminders, Notes, Messages, Contacts, Finder). "
            "AX snapshots, screen capture, OCR, and Spotlight are READ-ONLY. "
            "osa_exec and the Apple app tools can perform actions/writes — treat them as "
            "authoritative input, not previews. For reliable click/type/key automation use "
            "cua-driver instead."
        ),
    )

    register_ax_tools(mcp)
    register_vision_tools(mcp)
    register_osa_tools(mcp)
    register_apple_tools(mcp)

    return mcp
