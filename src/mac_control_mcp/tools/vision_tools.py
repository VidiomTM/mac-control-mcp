"""Vision (screenshot + OCR) tool registration."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP


def register_vision_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    def screen_capture(
        display: int = 0,
        region: list[int] | None = None,
        window_id: int | None = None,
        scale: float = 1.0,
        format: str = "png",
    ) -> dict[str, Any]:
        """
        Capture screen as base64-encoded image.
        region: [x, y, width, height] for partial capture.
        scale: 0.5 halves resolution (reduces tokens for vision models).
        Returns: {data: base64, format, width, height, size_bytes}
        """
        from mac_control_mcp.vision.capture import capture_screen

        region_tuple = tuple(region) if region else None
        return capture_screen(
            display=display,
            region=region_tuple,
            window_id=window_id,
            scale=scale,
            format=format,
        )

    @mcp.tool()
    def screen_ocr(
        region: list[int] | None = None,
        image_b64: str | None = None,
    ) -> str:
        """
        OCR text from screen region or provided base64 image.
        Returns: {text: full_text, observations: [{text, confidence, bbox}], count}

        This is the complement to cua-driver for apps whose AX surface is blank
        (Electron, canvas, games, Catalyst): capture + OCR produces text and
        word bounding boxes that can be turned into click targets outside this
        server (e.g. feed the center of an OCR bbox to cua-driver's px click).
        """
        from mac_control_mcp.vision.ocr import ocr_image_b64, ocr_screen_region

        if image_b64:
            result = ocr_image_b64(image_b64)
        else:
            region_tuple = tuple(region) if region else None
            result = ocr_screen_region(region=region_tuple)
        return json.dumps(result)
