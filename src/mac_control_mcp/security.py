"""Minimal security baseline: forbidden OSA patterns."""

import re

_FORBIDDEN_OSA = re.compile(
    r"(do\s+shell\s+script\s+.*?(rm\s+-[rf]+\s+/|sudo|dd\s+if=))",
    re.IGNORECASE | re.DOTALL,
)


def check_osa_script(script: str) -> None:
    m = _FORBIDDEN_OSA.search(script)
    if m:
        raise ValueError(f"Forbidden OSA pattern: {m.group()!r}")
