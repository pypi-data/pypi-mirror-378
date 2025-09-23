"""Command line helpers for deploying the .spec-dev template."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from textwrap import dedent

from . import __version__, complete_cycle, copy, create_memory
from .tasks_manifest import cmd_build_manifest
from .tasks_board import set_task_status
from .memories import check_memories


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage the packaged .spec-dev workspace template.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=dedent(
            """Examples:
            spec-dev
            spec-dev memory T-123
            spec-dev cycle --label fal-ai-image-gen"""
        ),
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

    cycle_parser = subparsers.add_parser(
        "cycle",
        help="Archive the current active artifacts and reset the workspace.",
    )
    cycle_parser.add_argument(
        "destination",
        nargs="?",
        default=".",
        help="Project directory containing .spec-dev (default: current directory)",
    )
    cycle_parser.add_argument(
        "--label",
        help="Optional label appended to the archived cycle directory name.",
    )
    cycle_parser.set_defaults(handler=_handle_cycle)
    manifest_parser = subparsers.add_parser(
        "tasks-manifest",
        help="Generate or display the planned file coverage manifest.",
    )
    manifest_parser.add_argument(
        "destination",
        nargs="?",
        default=".",
        help="Project directory containing .spec-dev (default: current directory)",
    )
    manifest_parser.add_argument(
        "--rewrite",
        action="store_true",
        help="Rewrite active-dev/file-coverage.json with the latest task definitions.",
    )
    manifest_parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that all task paths are well-formed and non-duplicated.",
    )
    manifest_parser.add_argument(
        "--auto-scope",
        action="store_true",
        help=(
            "Infer region selectors for duplicate file paths so multiple tasks can"
            " safely target different parts of the same file."
        ),
    )
    manifest_parser.set_defaults(handler=_handle_tasks_manifest)

    status_parser = subparsers.add_parser(
        "tasks-status",
        help="Update the status of a task card (pending, in-progress, done).",
    )
    status_parser.add_argument(
        "task_id",
        help="Task identifier (e.g. T-107).",
    )
    status_parser.add_argument(
        "--set",
        required=True,
        choices=["pending", "in-progress", "done"],
        help="Status to apply to the task card.",
    )
    status_parser.add_argument(
        "destination",
        nargs="?",
        default=".",
        help="Project directory containing .spec-dev (default: current directory)",
    )
    status_parser.set_defaults(handler=_handle_tasks_status)

    memories_parser = subparsers.add_parser(
        "memories",
        help="Check or scaffold task memory files for completed tasks.",
    )
    memories_parser.add_argument(
        "destination",
        nargs="?",
        default=".",
        help="Project directory containing .spec-dev (default: current directory)",
    )
    memories_parser.add_argument(
        "--ensure",
        action="store_true",
        help="Create memory stubs for done tasks that are missing entries.",
    )
    memories_parser.set_defaults(handler=_handle_memories)

    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        argv = ["init"]
    elif argv[0] not in {"init", "memory", "cycle", "tasks-manifest", "tasks-status", "memories"} and not argv[0].startswith("-"):
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


def _handle_cycle(args: argparse.Namespace) -> int:
    destination = Path(args.destination)
    archived = complete_cycle(destination, label=args.label)
    print(
        f"Archived active artifacts to {archived} and reset active-dev and active-memories"
    )
    return 0





def _handle_tasks_status(args: argparse.Namespace) -> int:
    destination = Path(args.destination)
    set_task_status(destination, args.task_id, args.set)
    print(
        f"Set {args.task_id} status to {args.set}. Run spec-dev tasks-manifest --rewrite --check to refresh coverage."
    )
    return 0


def _handle_memories(args: argparse.Namespace) -> int:
    destination = Path(args.destination)
    report = check_memories(destination, ensure=args.ensure)
    if report.created:
        for task_id in report.created:
            print(f"Created memory stub for {task_id}")
    if report.missing:
        for task_id in report.missing:
            print(f"[!] Missing memory for {task_id}")
        raise ValueError("Some completed tasks are missing memory entries")
    if not report.created and not report.missing:
        print("All completed tasks have memory entries.")
    return 0


def _handle_tasks_manifest(args: argparse.Namespace) -> int:
    destination = Path(args.destination)
    manifest = cmd_build_manifest(destination, auto_scope=args.auto_scope)
    if args.check:
        issues = manifest.validate()
        if issues:
            for issue in issues:
                print(f"[!] {issue}")
            sys.exit(1)
    if args.rewrite:
        manifest.write()
        print(f"Wrote manifest to {manifest.path}")
    else:
        print(json.dumps(manifest.to_dict(), indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
