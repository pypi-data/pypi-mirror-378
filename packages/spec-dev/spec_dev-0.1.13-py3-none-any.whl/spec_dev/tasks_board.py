from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
from typing import Dict, List

_SPEC_ROOT = Path('.spec-dev')
_TASKS_PATH = _SPEC_ROOT / 'active-dev' / 'active-tasks.md'

_STATUS_HEADERS = {
    'backlog': '## Backlog',
    'in-progress': '## In Progress',
    'done': '## Done',
}
_STATUS_ORDER = ['backlog', 'in-progress', 'done']
_TASK_HEADER = re.compile(r'^###\s+(T-\d{3})')


@dataclass
class TaskBlock:
    task_id: str
    lines: List[str]


@dataclass
class TaskBoard:
    path: Path
    project_root: Path
    prefix_lines: List[str]
    suffix_lines: List[str]
    section_static: Dict[str, List[str]]
    tasks: Dict[str, List[TaskBlock]]
    status_order: List[str]

    def ensure_status(self, status: str) -> None:
        if status not in self.section_static:
            self.section_static[status] = []
        if status not in self.tasks:
            self.tasks[status] = []
        if status not in self.status_order:
            self.status_order.append(status)

    def remove_task(self, task_id: str) -> tuple[str, TaskBlock] | None:
        for status in self.status_order:
            blocks = self.tasks.get(status, [])
            for index, block in enumerate(blocks):
                if block.task_id == task_id:
                    removed = blocks.pop(index)
                    return status, removed
        return None

    def add_task(self, status: str, block: TaskBlock) -> None:
        self.ensure_status(status)
        self.tasks[status].append(block)

    def to_lines(self) -> List[str]:
        lines: List[str] = []
        lines.extend(self.prefix_lines)
        if lines and lines[-1].strip():
            lines.append('')

        for status in _STATUS_ORDER:
            if status not in self.status_order:
                self.status_order.append(status)
        # keep explicit ordering while preserving new statuses
        seen = set()
        ordered_statuses: List[str] = []
        for status in _STATUS_ORDER:
            if status in self.status_order and status not in seen:
                ordered_statuses.append(status)
                seen.add(status)
        for status in self.status_order:
            if status not in seen:
                ordered_statuses.append(status)
                seen.add(status)

        for status in ordered_statuses:
            header = _STATUS_HEADERS.get(status, f'## {status.title()}')
            lines.append(header)
            lines.append('')

            static_lines = self.section_static.get(status, [])
            if static_lines:
                lines.extend(static_lines)
                if static_lines[-1].strip():
                    lines.append('')

            for block in self.tasks.get(status, []):
                lines.extend(block.lines)
                if block.lines and block.lines[-1].strip():
                    lines.append('')

            if lines and lines[-1].strip():
                lines.append('')

        if lines and not lines[-1].strip():
            lines.pop()
        lines.extend(self.suffix_lines)
        return lines

    def write(self, path: Path) -> None:
        text = '\n'.join(self.to_lines()).rstrip() + '\n'
        path.write_text(text)


def load_board(root: Path | None = None) -> tuple[TaskBoard, Path]:
    base = Path(root).expanduser().resolve() if root else Path.cwd()
    tasks_path = base / _TASKS_PATH
    if not tasks_path.exists():
        raise FileNotFoundError(f"Tasks file not found: {tasks_path}")

    lines = tasks_path.read_text().splitlines()
    prefix: List[str] = []
    suffix: List[str] = []
    section_static: Dict[str, List[str]] = {}
    tasks: Dict[str, List[TaskBlock]] = {}
    status_order: List[str] = []

    current_status: str | None = None
    current_block: TaskBlock | None = None
    in_suffix = False

    def finalize_block() -> None:
        nonlocal current_block
        if current_block is not None and current_status is not None:
            tasks.setdefault(current_status, []).append(current_block)
            current_block = None

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if in_suffix:
            suffix.append(raw_line)
            continue

        if stripped.startswith('Gate:'):
            finalize_block()
            in_suffix = True
            suffix.append(raw_line)
            continue

        status_from_header = None
        for status, header in _STATUS_HEADERS.items():
            if stripped == header:
                status_from_header = status
                break

        if status_from_header is not None:
            finalize_block()
            current_status = status_from_header
            if current_status not in status_order:
                status_order.append(current_status)
            section_static.setdefault(current_status, [])
            tasks.setdefault(current_status, [])
            continue

        if current_status is None:
            prefix.append(raw_line)
            continue

        header_match = _TASK_HEADER.match(stripped)
        if header_match:
            finalize_block()
            current_block = TaskBlock(task_id=header_match.group(1), lines=[raw_line])
            continue

        if current_block is not None:
            current_block.lines.append(raw_line)
        else:
            section_static.setdefault(current_status, []).append(raw_line)

    finalize_block()

    board = TaskBoard(
        path=tasks_path,
        project_root=base,
        prefix_lines=prefix,
        suffix_lines=suffix,
        section_static=section_static,
        tasks=tasks,
        status_order=status_order,
    )
    for status in _STATUS_ORDER:
        board.ensure_status(status)
    return board, tasks_path


def move_task(root: Path | None, task_id: str, target_status: str) -> Path:
    board, tasks_path = load_board(root)
    result = board.remove_task(task_id)
    if result is None:
        raise ValueError(f"Task {task_id} not found in active board")

    _, block = result
    board.add_task(target_status, block)
    board.write(tasks_path)
    return tasks_path
