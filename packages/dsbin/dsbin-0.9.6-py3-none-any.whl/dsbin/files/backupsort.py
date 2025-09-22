#!/usr/bin/env python3

"""Sorts saved backup files by adding a timestamp suffix to the filename.

This script is designed to sort backup files by adding a timestamp suffix to the filename.
This was originally created for dealing with a large number of SQL dumps and backups being
downloaded with the same filename, but it can be used for any type of file.
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import TYPE_CHECKING

from natsort import natsorted
from polykit import PolyArgs
from polykit.cli import confirm_action
from polykit.core import polykit_setup
from polykit.env import PolyEnv
from polykit.text import color

if TYPE_CHECKING:
    import argparse

polykit_setup()

env = PolyEnv()
env.add_var("BACKUPSORT_PATH", description="Path to move renamed files to")


def is_already_renamed(filename: str) -> int:
    """Check if the file already contains a timestamp matching the suffix format."""
    timestamp_patterns = re.findall(r"_\d{6}_\d{4}", filename)
    return len(timestamp_patterns)


def format_timestamp(file_path: str) -> str:
    """Get the last modification time of a file and format it as a string."""
    mtime = Path(file_path).stat().st_mtime
    return time.strftime("%y%m%d_%H%M", time.localtime(mtime))


def split_filename(filename: str) -> tuple[str, str]:
    """Split a filename into base name and full extension, preserving multi-level extensions.

    Args:
        filename: The filename to split.

    Returns:
        A tuple of (base_name, extension).
    """
    # Handle special cases like '.hidden' files
    if filename.startswith(".") and "." not in filename[1:]:
        return filename, ""

    # Split on the first dot, then join remaining parts
    parts = filename.split(".")
    if len(parts) <= 1:
        return filename, ""

    base = parts[0]
    extension = ".".join(["", *parts[1:]])  # Prepend empty string to add leading dot
    return base, extension


def clean_filename(filename: str, timestamp_count: int) -> str:
    """Clean a filename by removing unwanted patterns.

    Includes ".dump", " copy", "(1)", dates in "_YYYY-MM-DD" format, and extra spaces.

    Args:
        filename: The filename to clean.
        timestamp_count: The number of timestamp suffixes found.
    """
    # Split filename to preserve full extension
    base_name, extension = split_filename(filename)

    # Clean the base name
    clean_basename = re.sub(r"\.dump", "", base_name)
    clean_basename = re.sub(r"\s*\bcopy\b\s*\d*|\(\d+\)|_\d{4}-\d{2}-\d{2}", "", clean_basename)

    if timestamp_count > 1:
        clean_basename = re.sub(r"_\d{6}_\d{4}(?=_\d{6}_\d{4})", "", clean_basename)

    # Recombine with original extension
    clean_basename = re.sub(r"\s+", " ", clean_basename).strip()
    return f"{clean_basename}{extension}"


def get_files_to_process(args: argparse.Namespace) -> list[str]:
    """Get the list of files to process based on command line arguments."""
    files_to_process = args.files or ["./*"]
    expanded_files = []
    for file_pattern in files_to_process:
        if matches := list(Path().glob(str(file_pattern))):
            expanded_files.extend(str(path) for path in matches)
        else:
            print(color(f"No files found matching '{file_pattern}'", "yellow"))

    return natsorted(set(expanded_files))


def process_file(filename: str, auto: bool = False) -> tuple[str, str] | None:
    """Process a single file and return planned changes if any."""
    if filename.startswith(".") or not Path(filename).is_file():
        return None

    timestamp_count = is_already_renamed(filename)

    if timestamp_count == 0:
        formatted_timestamp = format_timestamp(filename)
        clean_name = clean_filename(filename, timestamp_count)
        base_name, extension = split_filename(clean_name)
        new_name = f"{base_name}_{formatted_timestamp}{extension}"
        if not auto:
            print(color(filename, "blue") + " ➔ " + color(new_name, "green"))
        return filename, new_name

    if timestamp_count >= 1:
        if timestamp_count == 1:
            print(color(filename, "yellow") + " has already been renamed, skipping.")
            return None

        print(color(filename, "red") + " was renamed multiple times, trimming extra timestamps.")
        clean_name = clean_filename(filename, timestamp_count)
        base_name, extension = split_filename(clean_name)
        new_name = f"{base_name}{extension}"
        if not auto:
            print(color(filename, "blue") + " ➔ " + color(new_name, "green"))
        return filename, new_name


def perform_operations(planned_changes: list[tuple[str, str]], args: argparse.Namespace) -> None:
    """Execute the planned changes if confirmed by the user."""
    if planned_changes and (args.y or confirm_action("Proceed with renaming?")):
        for old_name, new_name in planned_changes:
            old_path = Path(old_name)

            if not args.rename_only:
                final_path = Path(env.backupsort_path) / new_name
                action_str = "Renamed and moved"
            else:
                final_path = Path(new_name)
                action_str = "Renamed"

            old_path.rename(final_path)
            print(
                color(f"{action_str} {old_name}", "blue") + " ➔ " + color(str(final_path), "green")
            )
    elif planned_changes:
        print("Renaming canceled.")
    else:
        print("No files to rename.")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = PolyArgs(description=__doc__, lines=1)
    parser.add_argument("-y", action="store_true", help="proceed without confirmation")
    parser.add_argument(
        "--rename-only",
        action="store_true",
        help="only rename files, do not move to backup directory",
    )
    parser.add_argument(
        "files",
        nargs="*",
        default=[],
        help="files or wildcards to process (default: current directory)",
    )
    return parser.parse_args()


def main() -> None:
    """Rename and move files based on the command-line arguments."""
    args = parse_arguments()
    files = get_files_to_process(args)
    changes = [result for filename in files if (result := process_file(filename, args.y))]

    perform_operations(changes, args)


if __name__ == "__main__":
    main()
