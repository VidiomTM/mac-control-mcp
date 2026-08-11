"""AX (Accessibility) tool registration."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP


def register_ax_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    def ax_snapshot(
        app: str | None = None,
        max_depth: int = 8,
        budget_chars: int = 12000,
    ) -> str:
        """
        Snapshot the macOS accessibility tree for an app (or system-wide).

        This is a READ-ONLY observation tool. It traverses the AX tree via
        AXUIElementCopyAttributeValue and never posts input or steals focus.

        Use it where cua-driver's window-mapped AX resolver cannot bind the
        target: Catalyst/iOS apps, AppleSystemUIService panes, and apps whose
        window is not the frontmost AXWindow. cua-driver returns an EMPTY tree
        (degraded:true, ax_unresolved) for those; this tool walks the RAW
        system-wide tree by app name instead.

        Returns pruned JSON with element roles, labels, values, and screen
        coords. Coordinates can be fed to cua-driver clicks (in pixels) — this
        tool never posts input and never steals focus.
        """
        from mac_control_mcp.ax.snapshot import snapshot_app
        from mac_control_mcp.truncate import prune_tree, trim_to_budget

        raw = snapshot_app(app, max_depth=max_depth)
        pruned = prune_tree(raw, max_depth=max_depth, budget_chars=budget_chars) or {}
        trimmed = trim_to_budget(pruned, budget_chars=budget_chars)
        return json.dumps(trimmed, ensure_ascii=False)
