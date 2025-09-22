"""Utilities for distributing the .spec-dev workspace template."""
from __future__ import annotations

from contextlib import contextmanager
from importlib import resources
from pathlib import Path
import shutil

__all__ = ["copy", "template_dir"]
__version__ = "0.1.0"


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
    dest_path = Path(destination).expanduser().resolve()
    if not dest_path.exists():
        raise FileNotFoundError(f"Destination directory does not exist: {dest_path}")
    if not dest_path.is_dir():
        raise NotADirectoryError(f"Destination is not a directory: {dest_path}")

    target_dir = dest_path / ".spec-dev"
    if target_dir.exists() and not overwrite:
        raise FileExistsError(
            ".spec-dev already exists; pass overwrite=True to replace it."
        )

    source = resources.files("spec_dev.data") / ".spec-dev"
    with resources.as_file(source) as source_dir:
        shutil.copytree(Path(source_dir), target_dir, dirs_exist_ok=overwrite)

    return target_dir
