from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import List

_SPEC_ROOT = Path('.spec-dev')
_TASKS_PATH = _SPEC_ROOT / 'active-dev' / 'active-tasks.md'

_TASK_HEADER = re.compile(r'^###\s+(T-\d{3})\b')
_STATUS_LINE = re.compile(r'^\*\*Status:\*\*\s*(?P<value>\w+)', re.IGNORECASE)


@dataclass
class TaskBlock:
    task_id: str
    lines: List[str]

    def set_status(self, status: str) -> None:
        status_line = f"**Status:** {status}"
        for idx, line in enumerate(self.lines[1:], start=1):
            if _STATUS_LINE.match(line.strip()):
                self.lines[idx] = status_line
                return
            if line.startswith('**Why') or line.startswith('**Acceptance'):
                self.lines.insert(idx, status_line)
                return
        self.lines.append(status_line)

    def get_status(self) -> str:
        for line in self.lines:
            match = _STATUS_LINE.match(line.strip())
            if match:
                return match.group('value').lower()
        return 'pending'


@dataclass
class TaskBoard:
    path: Path
    project_root: Path
    prefix_lines: List[str]
    suffix_lines: List[str]
    tasks: List[TaskBlock]

    def write(self) -> None:
        lines: List[str] = []
        lines.extend(self.prefix_lines)
        if lines and lines[-1].strip():
            lines.append('')
        for block in self.tasks:
            lines.extend(block.lines)
            if block.lines and block.lines[-1].strip():
                lines.append('')
        if lines and lines[-1].strip():
            lines.append('')
        lines.extend(self.suffix_lines)
        text = '\n'.join(lines).rstrip() + '\n'
        self.path.write_text(text)


def load_board(destination: Path | None = None) -> TaskBoard:
    root = Path(destination).expanduser().resolve() if destination else Path.cwd()
    tasks_path = root / _TASKS_PATH
    if not tasks_path.exists():
        raise FileNotFoundError(f"Tasks file not found: {tasks_path}")

    lines = tasks_path.read_text().splitlines()
    prefix: List[str] = []
    suffix: List[str] = []
    tasks: List[TaskBlock] = []

    current_block: TaskBlock | None = None
    in_suffix = False

    def finalize_block() -> None:
        nonlocal current_block
        if current_block is not None:
            tasks.append(current_block)
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

        header_match = _TASK_HEADER.match(stripped)
        if header_match:
            finalize_block()
            current_block = TaskBlock(task_id=header_match.group(1), lines=[raw_line])
            continue

        if current_block is not None:
            current_block.lines.append(raw_line)
        else:
            prefix.append(raw_line)

    finalize_block()

    return TaskBoard(
        path=tasks_path,
        project_root=root,
        prefix_lines=prefix,
        suffix_lines=suffix,
        tasks=tasks,
    )


def set_task_status(destination: Path | None, task_id: str, status: str) -> Path:
    board = load_board(destination)
    for block in board.tasks:
        if block.task_id == task_id:
            block.set_status(status)
            board.write()
            return board.path
    raise ValueError(f"Task {task_id} not found in active-tasks.md")
