"""Utilities for distributing the .spec-dev workspace template."""
from __future__ import annotations

from contextlib import contextmanager
from importlib import resources
from pathlib import Path
import re
import shutil

__all__ = ["copy", "template_dir", "create_memory"]
__version__ = "0.1.1"

_TASK_MEMORY_DIR = ".spec-dev/memories"
_TASK_MEMORY_TEMPLATE = f"{_TASK_MEMORY_DIR}/T-000-template.md"
_TASK_ID_PATTERN = re.compile(r"^T-(\d+)$", re.IGNORECASE)


@contextmanager
def template_dir() -> Path:
    """Yield the location of the packaged .spec-dev directory."""
    source = resources.files("spec_dev.data") / ".spec-dev"
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

    target_dir = dest_path / ".spec-dev"
    if target_dir.exists() and not overwrite:
        raise FileExistsError(
            ".spec-dev already exists; pass overwrite=True to replace it."
        )

    source = resources.files("spec_dev.data") / ".spec-dev"
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
    spec_dir = dest_path / ".spec-dev"
    if not spec_dir.exists():
        raise FileNotFoundError(
            f"No .spec-dev directory found in {dest_path}. Run copy() first."
        )

    memory_dir = spec_dir / "memories"
    if not memory_dir.exists():
        memory_dir.mkdir(parents=True)

    normalized_id = _normalise_task_id(task_id)
    target_file = memory_dir / f"{normalized_id}-memory.md"
    if target_file.exists() and not overwrite:
        raise FileExistsError(
            f"{target_file} already exists; pass overwrite=True to replace it."
        )

    template_resource = resources.files("spec_dev.data") / _TASK_MEMORY_TEMPLATE
    with resources.as_file(template_resource) as template_path:
        content = Path(template_path).read_text()

    content = content.replace("Task Memory: T-000", f"Task Memory: {normalized_id}")
    target_file.write_text(content)
    return target_file


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
