"""Utilities for distributing the .spec-dev workspace template."""
from __future__ import annotations

from contextlib import contextmanager
from importlib import resources
from pathlib import Path
import re
import shutil

__all__ = ["copy", "template_dir", "create_memory", "complete_cycle"]
__version__ = "0.2.2"

_SPEC_ROOT = ".spec-dev"
_TASK_MEMORY_DIR = "active-memories"
_TEMPLATE_MEMORIES_PATH = ("templates", "memories")
_TASK_MEMORY_TEMPLATE = "task-memory-template.md"
_HISTORY_DIR = "history"
_TASK_ID_PATTERN = re.compile(r"^T-(\d+)$", re.IGNORECASE)


@contextmanager
def template_dir() -> Path:
    """Yield the location of the packaged .spec-dev directory."""
    source = resources.files("spec_dev.data") / _SPEC_ROOT
    with resources.as_file(source) as path:
        yield Path(path)


def copy(destination: Path | str = Path.cwd(), *, overwrite: bool = False) -> Path:
    """Copy the bundled .spec-dev folder into *destination*.

    Args:
        destination: Directory that should receive the .spec-dev folder.
        overwrite: Overwrite an existing .spec-dev folder when set to True.

    Returns:
        Path to the copied .spec-dev directory.
    """
    dest_path = _validate_destination(destination)

    target_dir = dest_path / _SPEC_ROOT
    if target_dir.exists() and not overwrite:
        raise FileExistsError(
            ".spec-dev already exists; pass overwrite=True to replace it."
        )

    source = resources.files("spec_dev.data") / _SPEC_ROOT
    with resources.as_file(source) as source_dir:
        shutil.copytree(Path(source_dir), target_dir, dirs_exist_ok=overwrite)

    return target_dir


def create_memory(
    task_id: str,
    destination: Path | str = Path.cwd(),
    *,
    overwrite: bool = False,
) -> Path:
    """Create a task memory file from the packaged template.

    Args:
        task_id: Task identifier (e.g. ``T-107``).
        destination: Project directory containing the `.spec-dev` folder.
        overwrite: Replace the memory file if it already exists.

    Returns:
        Path to the created memory file.
    """
    dest_path = _validate_destination(destination)
    spec_dir = dest_path / _SPEC_ROOT
    if not spec_dir.exists():
        raise FileNotFoundError(
            f"No .spec-dev directory found in {dest_path}. Run copy() first."
        )

    memory_dir = spec_dir / _TASK_MEMORY_DIR
    if not memory_dir.exists():
        memory_dir.mkdir(parents=True)

    normalized_id = _normalise_task_id(task_id)
    target_file = memory_dir / f"{normalized_id}-memory.md"
    if target_file.exists() and not overwrite:
        raise FileExistsError(
            f"{target_file} already exists; pass overwrite=True to replace it."
        )

    template_resource = resources.files("spec_dev.data") / _SPEC_ROOT
    for part in _TEMPLATE_MEMORIES_PATH:
        template_resource = template_resource / part
    template_resource = template_resource / _TASK_MEMORY_TEMPLATE
    with resources.as_file(template_resource) as template_path:
        content = Path(template_path).read_text()

    content = content.replace("Task Memory: T-000", f"Task Memory: {normalized_id}")
    target_file.write_text(content)
    return target_file


def complete_cycle(
    destination: Path | str = Path.cwd(),
    *,
    label: str | None = None,
) -> Path:
    """Archive the current active artifacts and reset the workspace.

    Args:
        destination: Project directory containing the `.spec-dev` folder.
        label: Optional label appended to the archived cycle directory name.

    Returns:
        Path to the archived cycle directory.
    """
    dest_path = _validate_destination(destination)
    spec_dir = dest_path / _SPEC_ROOT
    if not spec_dir.exists():
        raise FileNotFoundError(
            f"No .spec-dev directory found in {dest_path}. Run copy() first."
        )

    active_dir = spec_dir / "active-dev"
    if not active_dir.exists():
        raise FileNotFoundError(
            "active-dev directory not found; nothing to archive."
        )

    memory_dir = spec_dir / _TASK_MEMORY_DIR

    history_root = spec_dir / _HISTORY_DIR
    history_root.mkdir(exist_ok=True)

    cycle_name = _generate_cycle_name(label)
    cycle_dir = history_root / cycle_name
    cycle_dir.mkdir()

    for item in list(active_dir.iterdir()):
        target = cycle_dir / item.name
        if item.is_dir():
            shutil.move(str(item), target)
        else:
            shutil.move(str(item), target)

    if memory_dir.exists():
        cycle_memory_dir = cycle_dir / _TASK_MEMORY_DIR
        cycle_memory_dir.mkdir()
        for item in list(memory_dir.iterdir()):
            shutil.move(str(item), cycle_memory_dir / item.name)

    _restore_active_memories(memory_dir)
    _restore_active_templates(active_dir)

    return cycle_dir


def _validate_destination(destination: Path | str) -> Path:
    dest_path = Path(destination).expanduser().resolve()
    if not dest_path.exists():
        raise FileNotFoundError(f"Destination directory does not exist: {dest_path}")
    if not dest_path.is_dir():
        raise NotADirectoryError(f"Destination is not a directory: {dest_path}")
    return dest_path


def _normalise_task_id(task_id: str) -> str:
    match = _TASK_ID_PATTERN.match(task_id.strip())
    if not match:
        raise ValueError(
            "Task ID must match the pattern T-### (e.g. T-107)."
        )
    value = int(match.group(1))
    return f"T-{value:03d}"


def _generate_cycle_name(label: str | None) -> str:
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if not label:
        return f"{timestamp}"

    slug = re.sub(r"[^a-z0-9-]+", "-", label.strip().lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return f"{timestamp}-{slug}" if slug else timestamp


def _restore_active_templates(active_dir: Path) -> None:
    if not active_dir.exists():
        active_dir.mkdir(parents=True)

    template_resource = resources.files("spec_dev.data") / _SPEC_ROOT / "active-dev"
    with resources.as_file(template_resource) as template_path:
        source = Path(template_path)
        for item in source.iterdir():
            target = active_dir / item.name
            if item.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)


def _restore_active_memories(memory_dir: Path) -> None:
    template_resource = resources.files("spec_dev.data") / _SPEC_ROOT / _TASK_MEMORY_DIR
    with resources.as_file(template_resource) as template_path:
        source = Path(template_path)
        if memory_dir.exists():
            shutil.rmtree(memory_dir)
        shutil.copytree(source, memory_dir)
