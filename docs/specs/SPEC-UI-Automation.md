---
checksum: eb2a30871f0e175b6bb0ec1b9fa70349417913ccc45c40539719f88c9027a003
---
# SPEC: macOS UI Automation

**Version:** 0.2.0
**Status:** Accepted
**Date:** 2026-05-17 (v0.2: 2026-08-11)

## Purpose

Define how mac-control-mcp observes macOS UI across AX, Vision, and OSA layers —
**as a read-only complement to cua-driver**. This server never posts input.

## Division of labor with cua-driver

| Capability | Owned by |
|---|---|
| Background click / type / scroll / hotkey (no focus steal) | cua-driver |
| Window list + state + verify-by-resnapshot | cua-driver |
| AX tree snapshot (window-mapped) | cua-driver `get_window_state` |
| RAW AX tree snapshot by app name (Catalyst / iOS-on-Mac / AppleSystemUIService) | this server `ax_snapshot` |
| Screen capture + on-device OCR | this server `screen_capture`, `screen_ocr` |
| AppleScript/JXA + Apple-app data access | this server (OSA KB) |
| Spotlight / mdfind file search | this server `spotlight_query` |

## Observation Layers

### Layer 1: Accessibility (AX) — read-only snapshot

```txt
ax_snapshot(app="Tapo", max_depth=8, budget_chars=12000)
  → snapshot_app() traverses AX tree via AXUIElementCopyAttributeValue (by app name)
  → _element_to_dict() recursively builds {role, title, value, frame, children}
  → prune_tree() removes nodes with disallowed roles (if no children), enforces depth cap
  → trim_to_budget() BFS-trims: drops deepest children first to fit token budget
  → returns JSON string
```

The returned frames are screen coordinates; feed them to cua-driver clicks (px rung).

**Removed (cua-driver owns):** `ax_click`, `ax_type`, `ax_scroll`, `ax_hotkey`,
`ax_system_ui` — these used global CGEvent taps that posted into the frontmost
app and stole focus, and duplicated cua-driver's backgrounded action layer.

### Layer 2: Vision/OCR

Fallback for Electron apps, games, or any app without AX support.

```txt
screen_capture(region=[x,y,w,h], scale=0.5, format="png")
  → screencapture CLI with -R or -l or -D flags
  → optional PIL rescale for token efficiency
  → base64-encoded image data returned

screen_ocr(region=[x,y,w,h] | image_b64=...)
  → VNRecognizeTextRequest (on-device Vision.framework)
  → returns text, per-observation confidence + bbox
  → AppleScript fallback when Vision framework unavailable
```

OCR bounding boxes are the click targets for cua-driver's px rung on AX-empty
surfaces (Electron/canvas/games).

**Removed (cua-driver owns):** `screen_list_windows` (cua-driver `list_windows`),
`screen_wait_for_change` (cua-driver verify-by-resnapshot loop; the MD5-whole-
screenshot heuristic was brittle).

### Layer 3: AppleScript/JXA (OSA)

For native Apple app data where AX/Vision are insufficient.

```txt
osa_search(query="send email", app="Mail")
  → fuzzy match against YAML KB entries
  → returns ranked results with IDs, summaries, args

osa_run(kb_id="mail_compose_send", args=["to", "subj", "body"])
  → load script from YAML KB
  → execute via osascript list-args subprocess
  → security validation (no destructive patterns)

osa_exec(script="...", lang="applescript")
  → raw script execution with security validation
  → only for edge cases where KB lacks the needed script
```

## Security

- `check_osa_script()` blocks `rm -rf /`, `sudo`, `dd if=` in OSA scripts
- KB scripts are vetted — only `osa_exec` allows arbitrary scripts
- All subprocess calls are list-form (no shell injection)
