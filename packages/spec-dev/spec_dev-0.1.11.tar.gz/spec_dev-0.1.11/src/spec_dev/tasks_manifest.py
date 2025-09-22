from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
from pathlib import Path

SPEC_ROOT = Path('.spec-dev')
TASKS_FILE = SPEC_ROOT / 'active-dev' / 'active-tasks.md'
MANIFEST_FILE = SPEC_ROOT / 'active-dev' / 'file-coverage.json'

_TASK_HEADER = re.compile(r'^### (T-\d{3})')
_CHANGES_FENCE = re.compile(r'^```changes$', re.IGNORECASE)


@dataclass
class ManifestEntry:
    task_id: str
    operations: list[dict[str, str]] = field(default_factory=list)


@dataclass
class Manifest:
    root: Path
    entries: list[ManifestEntry]

    @property
    def path(self) -> Path:
        return self.root / MANIFEST_FILE

    def to_dict(self) -> dict:
        return {
            "entries": [
                {
                    "task_id": entry.task_id,
                    "operations": entry.operations,
                }
                for entry in self.entries
            ]
        }

    def write(self) -> None:
        target = self.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2) + "\n")

    def validate(self) -> list[str]:
        issues: list[str] = []
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


def cmd_build_manifest(destination: Path) -> Manifest:
    root = destination.expanduser().resolve()
    tasks_file = root / TASKS_FILE
    if not tasks_file.exists():
        raise FileNotFoundError(f"Tasks file not found: {tasks_file}")

    entries: list[ManifestEntry] = []
    current: ManifestEntry | None = None
    in_fence = False

    for raw_line in tasks_file.read_text().splitlines():
        line = raw_line.rstrip()
        header = _TASK_HEADER.match(line)
        if header:
            if current is not None:
                entries.append(current)
            current = ManifestEntry(task_id=header.group(1))
            in_fence = False
            continue

        stripped = line.strip()
        if stripped.startswith('```'):
            if _CHANGES_FENCE.match(stripped):
                in_fence = not in_fence
            else:
                in_fence = False
            continue

        if in_fence and current is not None and stripped:
            if ':' not in line or '->' not in line:
                continue
            path_part, rest = line.split(':', 1)
            op_part, detail = rest.split('->', 1)
            op = op_part.strip()
            path = path_part.strip()
            current.operations.append({
                "path": path,
                "operation": op.lower(),
                "detail": detail.strip(),
            })

    if current is not None:
        entries.append(current)

    return Manifest(root=root, entries=entries)
