"""Command line helpers for deploying the .spec-dev template."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, copy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Copy the packaged .spec-dev folder into a target directory.",
    )
    parser.add_argument(
        "destination",
        nargs="?",
        default=".",
        help="Directory that should receive the .spec-dev folder (default: current directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing .spec-dev directory if present.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"spec-dev {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    destination = Path(args.destination)
    try:
        target = copy(destination, overwrite=args.force)
    except FileExistsError as exc:
        parser.error(str(exc))
    except (FileNotFoundError, NotADirectoryError) as exc:
        parser.error(str(exc))

    print(f"Copied .spec-dev to {target}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
