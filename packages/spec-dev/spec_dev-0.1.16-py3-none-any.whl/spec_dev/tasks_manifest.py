from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import List

from .tasks_board import load_board, TaskBlock


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
        seen_paths: dict[str, str] = {}
        for entry in self.entries:
            for op in entry.operations:
                path = op["path"]
                if path in seen_paths and seen_paths[path] != entry.task_id:
                    issues.append(
                        f"Path {path} declared by multiple tasks: {seen_paths[path]} and {entry.task_id}"
                    )
                else:
                    seen_paths[path] = entry.task_id
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
        operations.append(
            {
                "path": path_part.strip(),
                "operation": op_part.strip().lower(),
                "detail": detail.strip(),
            }
        )
    return operations


def cmd_build_manifest(destination: Path | None) -> Manifest:
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
    return Manifest(root=board.project_root, entries=entries)
