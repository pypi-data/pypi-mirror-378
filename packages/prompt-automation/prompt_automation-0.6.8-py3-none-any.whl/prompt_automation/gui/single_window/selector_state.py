from __future__ import annotations

"""Selector UI state persistence (expanded folders) in gui-settings.json."""

import json
from pathlib import Path
from typing import Iterable, Set

from .geometry import SETTINGS_PATH


def _canon(rel: str) -> str:
    parts = [p for p in Path(str(rel)).parts if p]
    return "/".join(parts)


def load_expanded() -> Set[str]:
    try:
        if SETTINGS_PATH.exists():
            data = json.loads(SETTINGS_PATH.read_text()) or {}
            raw = data.get("selector_expanded")
            if isinstance(raw, list):
                return {_canon(str(x)) for x in raw if isinstance(x, (str, int))}
    except Exception:
        pass
    return set()


def save_expanded(paths: Iterable[str]) -> None:
    try:  # pragma: no cover - best effort persistence
        cur = {}
        if SETTINGS_PATH.exists():
            try:
                cur = json.loads(SETTINGS_PATH.read_text()) or {}
            except Exception:
                cur = {}
        lst = sorted({_canon(p) for p in paths if p})
        if lst:
            cur["selector_expanded"] = lst
        else:
            cur.pop("selector_expanded", None)
        SETTINGS_PATH.write_text(json.dumps(cur, indent=2))
    except Exception:
        pass


__all__ = ["load_expanded", "save_expanded"]
