"""Command line helpers for deploying the .spec-dev template."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, copy, create_memory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage the packaged .spec-dev workspace template.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"spec-dev {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser(
        "init",
        help="Copy the .spec-dev folder into the target directory.",
    )
    init_parser.add_argument(
        "destination",
        nargs="?",
        default=".",
        help="Directory that should receive the .spec-dev folder (default: current directory)",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing .spec-dev directory if present.",
    )
    init_parser.set_defaults(handler=_handle_init)

    memory_parser = subparsers.add_parser(
        "memory",
        help="Create a task memory file from the template.",
    )
    memory_parser.add_argument(
        "task_id",
        help="Task identifier (e.g. T-107).",
    )
    memory_parser.add_argument(
        "destination",
        nargs="?",
        default=".",
        help="Project directory containing .spec-dev (default: current directory)",
    )
    memory_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing memory file if present.",
    )
    memory_parser.set_defaults(handler=_handle_memory)

    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv or argv[0] not in {"init", "memory"}:
        argv = ["init", *argv]

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.handler(args)
    except FileExistsError as exc:
        parser.error(str(exc))
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        parser.error(str(exc))


def _handle_init(args: argparse.Namespace) -> int:
    destination = Path(args.destination)
    target = copy(destination, overwrite=args.force)
    print(f"Copied .spec-dev to {target}")
    return 0


def _handle_memory(args: argparse.Namespace) -> int:
    destination = Path(args.destination)
    memory_file = create_memory(args.task_id, destination, overwrite=args.overwrite)
    print(f"Created task memory at {memory_file}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
