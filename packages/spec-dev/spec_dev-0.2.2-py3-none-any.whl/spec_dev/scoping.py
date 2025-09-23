from __future__ import annotations

"""Heuristics for auto-scoping duplicate path operations to regions.

This module avoids heavy dependencies. It derives a selector from the
operation's detail text using lightweight patterns. If the heuristic cannot
produce distinct selectors for all colliding ops, it leaves them unchanged so
validation can surface a real conflict.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
import re


_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_-]{2,}")


def _infer_from_detail(detail: str) -> str | None:
    text = detail.strip()
    if not text:
        return None

    # Look for common symbol patterns first
    for pat, prefix in [
        (re.compile(r"\bfn\s+([A-Za-z_][A-Za-z0-9_]*)"), "fn"),
        (re.compile(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)"), "fn"),
        (re.compile(r"\bimpl\s+([A-Za-z_][A-Za-z0-9_:]*)"), "impl"),
        (re.compile(r"\b(class|struct|enum|trait)\s+([A-Za-z_][A-Za-z0-9_]*)"), "type"),
        (re.compile(r"\b(mod|module)\s+([A-Za-z_][A-Za-z0-9_]*)"), "mod"),
        (re.compile(r"\bmethod\s+([A-Za-z_][A-Za-z0-9_]*)"), "fn"),
    ]:
        m = pat.search(text)
        if m:
            name = m.group(m.lastindex)  # last captured group
            return f"{prefix}:{name}"

    # Fallback: pick a significant token as a topic
    tokens = [t.lower() for t in _TOKEN_RE.findall(text)]
    stop = {"add", "update", "modify", "wire", "and", "the", "for", "to", "in", "of", "with"}
    for tok in tokens:
        if tok not in stop:
            return f"topic:{tok}"
    return None


@dataclass
class _OpRef:
    entry_idx: int
    op_idx: int
    task_id: str
    detail: str


def _find_collisions(manifest) -> dict[str, List[_OpRef]]:
    collisions: dict[str, List[_OpRef]] = {}
    path_counts: dict[str, int] = {}
    for eidx, entry in enumerate(manifest.entries):
        for oidx, op in enumerate(entry.operations):
            if op.get("selector", "*") == "*":
                path = op["path"].strip()
                path_counts[path] = path_counts.get(path, 0) + 1
    for path, count in path_counts.items():
        if count > 1:
            refs: List[_OpRef] = []
            for eidx, entry in enumerate(manifest.entries):
                for oidx, op in enumerate(entry.operations):
                    if op["path"].strip() == path and op.get("selector", "*") == "*":
                        refs.append(_OpRef(eidx, oidx, entry.task_id, op.get("detail", "")))
            collisions[path] = refs
    return collisions


def auto_scope_manifest(manifest) -> None:
    """Assign region selectors to unresolved duplicate path operations.

    Strategy:
    - For each path referenced by multiple wildcard operations, attempt to
      infer a distinct selector for each op using its detail text.
    - Only assign selectors when they are distinct across tasks; otherwise
      leave wildcard selectors as-is so validation still fails and surfaces a
      real coordination conflict.
    """
    collisions = _find_collisions(manifest)
    for path, refs in collisions.items():
        # Propose selectors
        proposed: list[str | None] = [_infer_from_detail(r.detail) for r in refs]
        # If any could not be inferred, skip this path
        if any(p is None for p in proposed):
            continue
        # If not all unique, skip to avoid masking a true overlap
        if len(set(proposed)) != len(proposed):
            continue

        # Apply selectors
        for ref, sel in zip(refs, proposed, strict=False):
            op = manifest.entries[ref.entry_idx].operations[ref.op_idx]
            op["selector"] = sel  # type: ignore[arg-type]

