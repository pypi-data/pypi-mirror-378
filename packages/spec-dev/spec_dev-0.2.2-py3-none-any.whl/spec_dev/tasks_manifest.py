from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import List

from .tasks_board import load_board, TaskBlock
from .scoping import auto_scope_manifest


@dataclass
class ManifestEntry:
    task_id: str
    status: str
    operations: List[dict[str, str]] = field(default_factory=list)


@dataclass
class Manifest:
    root: Path
    entries: List[ManifestEntry]

    @property
    def path(self) -> Path:
        return self.root / '.spec-dev' / 'active-dev' / 'file-coverage.json'

    def to_dict(self) -> dict:
        return {
            "entries": [
                {
                    "task_id": entry.task_id,
                    "status": entry.status,
                    "operations": entry.operations,
                }
                for entry in self.entries
            ]
        }

    def write(self) -> None:
        target = self.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2) + "\n")

    def validate(self) -> List[str]:
        issues: List[str] = []
        # Track per-path ownership with optional region selectors.
        # A wildcard selector ('*') conflicts with any other selector for the same path.
        seen: dict[str, dict[str, str]] = {}
        wildcard_owner: dict[str, str] = {}

        for entry in self.entries:
            for op in entry.operations:
                path = op["path"].strip()
                selector = op.get("selector", "*").strip() or "*"

                # Wildcard conflicts with any existing owner for the path.
                if selector == "*":
                    # If someone already owns the whole file and it's not us
                    owner = wildcard_owner.get(path)
                    if owner and owner != entry.task_id:
                        issues.append(
                            f"Path {path} declared by multiple tasks: {owner} and {entry.task_id}"
                        )
                        continue
                    # If specific regions already owned by others, conflict with each of them
                    for _sel, owner in (seen.get(path) or {}).items():
                        if owner != entry.task_id:
                            issues.append(
                                f"Path {path} declared by multiple tasks: {owner} and {entry.task_id}"
                            )
                    wildcard_owner[path] = entry.task_id
                    continue

                # Non-wildcard selector
                # If whole file already owned by someone else -> conflict
                owner = wildcard_owner.get(path)
                if owner and owner != entry.task_id:
                    issues.append(
                        f"Path {path} declared by multiple tasks: {owner} and {entry.task_id}"
                    )
                    continue

                owners = seen.setdefault(path, {})
                existing = owners.get(selector)
                if existing and existing != entry.task_id:
                    issues.append(
                        f"Path {path}@{selector} declared by multiple tasks: {existing} and {entry.task_id}"
                    )
                else:
                    owners[selector] = entry.task_id
        return issues


def _parse_operations(block: TaskBlock) -> List[dict[str, str]]:
    operations: List[dict[str, str]] = []
    in_fence = False
    for raw_line in block.lines:
        line = raw_line.strip()
        if line.startswith('```'):
            if line.lower() == '```changes':
                in_fence = not in_fence
            else:
                in_fence = False
            continue
        if not in_fence or not line:
            continue
        if ':' not in raw_line or '->' not in raw_line:
            continue
        path_part, rest = raw_line.split(':', 1)
        op_part, detail = rest.split('->', 1)

        # Optional region selector, appended as "@ <selector>" at the end of the line.
        selector = "*"
        det = detail.rstrip()
        # Require a separating space before '@' to reduce false positives.
        if " @" in det:
            det_head, det_tail = det.rsplit(" @", 1)
            if det_tail.strip():
                selector = det_tail.strip()
                det = det_head.rstrip()

        operations.append(
            {
                "path": path_part.strip(),
                "operation": op_part.strip().lower(),
                "detail": det.strip(),
                "selector": selector,
            }
        )
    return operations


def cmd_build_manifest(destination: Path | None, *, auto_scope: bool = False) -> Manifest:
    board = load_board(destination)
    entries: List[ManifestEntry] = []
    for block in board.tasks:
        entries.append(
            ManifestEntry(
                task_id=block.task_id,
                status=block.get_status(),
                operations=_parse_operations(block),
            )
        )
    manifest = Manifest(root=board.project_root, entries=entries)
    if auto_scope:
        auto_scope_manifest(manifest)
    return manifest
