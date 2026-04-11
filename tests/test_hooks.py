"""hooks: rekisteröinti ja emit."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_hooks_register_and_emit():
    import uuid

    import hooks

    name = f"test_evt_{uuid.uuid4().hex}"
    seen: list[int] = []

    def cb(x: int = 0, **_kwargs):
        seen.append(x)

    hooks.register(name, cb)
    hooks.emit(name, x=42)
    assert seen == [42]
