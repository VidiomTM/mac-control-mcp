"""Unit tests for vision modules with mocked dependencies."""

from __future__ import annotations

import sys
import unittest.mock as um

import pytest


@pytest.mark.unit
def test_capture_screen_subprocess_success(mocker):
    mock_run = mocker.patch("mac_control_mcp.vision.capture.subprocess.run")
    mock_run.return_value.returncode = 0
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"fake_data"))

    mock_img = mocker.MagicMock()
    mock_img.size = (100, 200)
    mock_img_module = mocker.MagicMock()
    mock_img_module.Image.open.return_value = mock_img
    mocker.patch.dict(sys.modules, {"PIL": mock_img_module})

    import mac_control_mcp.vision.capture as cap

    mocker.patch.object(cap, "os")
    cap.os.unlink = mocker.MagicMock()

    result = cap.capture_screen()
    assert result["format"] == "png"
    assert result["width"] == 100
    assert result["height"] == 200


@pytest.mark.unit
def test_capture_screen_subprocess_failure(mocker):
    mock_run = mocker.patch("mac_control_mcp.vision.capture.subprocess.run")
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = b"error"
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"data"))

    import mac_control_mcp.vision.capture as cap

    mocker.patch.object(cap, "os")
    cap.os.unlink = mocker.MagicMock()

    with pytest.raises(RuntimeError, match="screencapture failed"):
        cap.capture_screen()


@pytest.mark.unit
def test_capture_screen_with_region(mocker):
    mock_run = mocker.patch("mac_control_mcp.vision.capture.subprocess.run")
    mock_run.return_value.returncode = 0
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"data"))

    mock_img = mocker.MagicMock()
    mock_img.size = (50, 50)
    mock_img_module = mocker.MagicMock()
    mock_img_module.Image.open.return_value = mock_img
    mocker.patch.dict(sys.modules, {"PIL": mock_img_module})

    import mac_control_mcp.vision.capture as cap

    mocker.patch.object(cap, "os")
    cap.os.unlink = mocker.MagicMock()

    cap.capture_screen(region=(0, 0, 100, 100))
    cmd = mock_run.call_args[0][0]
    assert "-R" in cmd


@pytest.mark.unit
def test_capture_screen_with_window_id(mocker):
    mock_run = mocker.patch("mac_control_mcp.vision.capture.subprocess.run")
    mock_run.return_value.returncode = 0
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"data"))

    mock_img = mocker.MagicMock()
    mock_img.size = (50, 50)
    mock_img_module = mocker.MagicMock()
    mock_img_module.Image.open.return_value = mock_img
    mocker.patch.dict(sys.modules, {"PIL": mock_img_module})

    import mac_control_mcp.vision.capture as cap

    mocker.patch.object(cap, "os")
    cap.os.unlink = mocker.MagicMock()

    cap.capture_screen(window_id=123)
    cmd = mock_run.call_args[0][0]
    assert "-l" in cmd


@pytest.mark.unit
def test_capture_screen_jpg_format(mocker):
    mock_run = mocker.patch("mac_control_mcp.vision.capture.subprocess.run")
    mock_run.return_value.returncode = 0
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"data"))

    mock_img = mocker.MagicMock()
    mock_img.size = (50, 50)
    mock_img_module = mocker.MagicMock()
    mock_img_module.Image.open.return_value = mock_img
    mocker.patch.dict(sys.modules, {"PIL": mock_img_module})

    import mac_control_mcp.vision.capture as cap

    mocker.patch.object(cap, "os")
    cap.os.unlink = mocker.MagicMock()

    cap.capture_screen(format="jpg")
    cmd = mock_run.call_args[0][0]
    assert "-t" in cmd


@pytest.mark.unit
def test_capture_screen_with_scale(mocker):
    mock_run = mocker.patch("mac_control_mcp.vision.capture.subprocess.run")
    mock_run.return_value.returncode = 0
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"data"))

    mock_img = mocker.MagicMock()
    mock_img.size = (100, 200)
    mock_img_module = mocker.MagicMock()
    mock_img_module.Image.open.return_value = mock_img
    mocker.patch.dict(sys.modules, {"PIL": mock_img_module})

    mock_scale = mocker.patch("mac_control_mcp.vision.capture._scale_image")

    import mac_control_mcp.vision.capture as cap

    mocker.patch.object(cap, "os")
    cap.os.unlink = mocker.MagicMock()

    cap.capture_screen(scale=0.5)
    mock_scale.assert_called_once()


@pytest.mark.unit
def test_capture_screen_no_pil_fallback(mocker):
    mock_run = mocker.patch("mac_control_mcp.vision.capture.subprocess.run")
    mock_run.return_value.returncode = 0
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"data"))

    import mac_control_mcp.vision.capture as cap

    mocker.patch.object(cap, "os")
    cap.os.unlink = mocker.MagicMock()

    with um.patch("sys.modules", {"PIL": None}):
        import mac_control_mcp.vision.capture as cap_mod

        result = cap_mod.capture_screen()
        assert result["width"] is None
        assert result["height"] is None
