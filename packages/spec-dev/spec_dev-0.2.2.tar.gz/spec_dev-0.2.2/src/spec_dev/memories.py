from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from .tasks_manifest import cmd_build_manifest

_MEMORY_DIR = Path('.spec-dev/active-memories')
_TEMPLATE_FILE = Path('.spec-dev/templates/memories/task-memory-template.md')


@dataclass
class MemoryReport:
    root: Path
    missing: List[str] = field(default_factory=list)
    created: List[str] = field(default_factory=list)
    existing: List[str] = field(default_factory=list)

    @property
    def path(self) -> Path:
        return self.root / _MEMORY_DIR


def ensure_memory_stub(root: Path, task_id: str) -> bool:
    memory_dir = root / _MEMORY_DIR
    memory_dir.mkdir(parents=True, exist_ok=True)
    target = memory_dir / f"{task_id}-memory.md"
    if target.exists():
        return False

    template = root / _TEMPLATE_FILE
    if not template.exists():
        raise FileNotFoundError(f"Template not found: {template}")

    content = template.read_text()
    content = content.replace('Task Memory: T-000', f'Task Memory: {task_id}')
    target.write_text(content)
    return True


def check_memories(destination: Path | None = None, *, ensure: bool = False) -> MemoryReport:
    manifest = cmd_build_manifest(destination)
    root = manifest.root
    report = MemoryReport(root=root)
    memory_dir = report.path
    memory_dir.mkdir(parents=True, exist_ok=True)

    for entry in manifest.entries:
        task_id = entry.task_id
        memory_path = memory_dir / f"{task_id}-memory.md"
        if entry.status.lower() == 'done':
            if memory_path.exists():
                report.existing.append(task_id)
            elif ensure:
                created = ensure_memory_stub(root, task_id)
                if created:
                    report.created.append(task_id)
            else:
                report.missing.append(task_id)
    return report
