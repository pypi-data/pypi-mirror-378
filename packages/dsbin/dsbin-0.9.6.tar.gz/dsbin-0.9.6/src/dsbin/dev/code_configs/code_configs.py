"""Download configs for coding tools and compare against local versions.

This script is designed to download configuration files for various coding tools (e.g., ruff, mypy)
to compare against files with the same name in the directory where the script is run. This is to
ensure that I always have the latest versions of my preferred configurations for all my projects.

Note that these config files live in the dsbin repository: https://github.com/dannystewart/dsbin

The script also saves the updated config files to the package root, which is the root of the dsbin
repository itself, thereby creating a virtuous cycle where the repo is always up-to-date with the
latest versions of the config files for other projects to pull from.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

import requests
from polykit import PolyArgs, PolyLog
from polykit.cli import confirm_action
from polykit.files import PolyDiff
from polykit.text import color

if TYPE_CHECKING:
    import argparse


@dataclass
class ConfigFile:
    """Represents a config file that can be updated from a remote source."""

    BASE_URL: ClassVar[str] = "https://raw.githubusercontent.com/dannystewart"
    REPO: ClassVar[str] = "dsbin"
    FOLDER: ClassVar[str] = "configs"

    name: str
    extra: bool = False  # Extras are not included by default
    url: str = field(init=False)
    local_path: Path = field(init=False)
    post_update_command: str | list[str] | None = None

    def __post_init__(self):
        self.url = f"{self.BASE_URL}/{self.REPO}/refs/heads/main/{self.FOLDER}/{self.name}"
        self.local_path = Path.cwd() / self.name


# noinspection PyArgumentList
class ConfigManager:
    """Manages downloading and updating config files from a remote repository."""

    CONFIGS: ClassVar[list[ConfigFile]] = [
        ConfigFile("ruff.toml"),
        ConfigFile("mypy.ini"),
        ConfigFile(".github/workflows/docs.yml", extra=True),
        ConfigFile(".github/workflows/python-publish.yml", extra=True),
        ConfigFile(".pdoc/tokyo-night/syntax-highlighting.css", extra=True),
        ConfigFile(".pdoc/tokyo-night/theme.css", extra=True),
        ConfigFile(
            ".pre-commit-config.yaml",
            extra=True,
            post_update_command=["pre-commit", "uninstall", "&&", "pre-commit", "install"],
        ),
    ]

    def __init__(self, include_extras: bool = False, no_confirm: bool = False):
        self.logger = PolyLog.get_logger()
        self.no_confirm = no_confirm
        self.changes_made = set()
        self.skipped_dirs = set()  # Track rejected parent directories

        # Filter configs: always include standard files, include extras only if requested
        if include_extras:
            self.configs = self.CONFIGS  # Include all files
        else:
            self.configs = [config for config in self.CONFIGS if not config.extra]

        # Determine if all configs should be created by checking if any exist locally
        self.should_create_all = not any(config.local_path.exists() for config in self.configs)

        if self.should_create_all:
            self.logger.debug(
                "No existing configs found; downloading and creating all available configs."
            )

    def update_configs(self) -> None:
        """Pull down latest configs from repository, updating local copies."""
        skipped_configs = []

        for config in self.configs:
            remote_content = self.fetch_remote_content(config)
            if not remote_content:
                self.logger.error(
                    "Failed to update %s config as it was not available.", config.name
                )
                continue

            if self.process_config(config, remote_content):
                self.changes_made.add(config.name)
                # Run post-update command if specified and file was updated
                if config.post_update_command:
                    self.run_post_update_command(config)
            elif config.name not in self.changes_made:
                skipped_configs.append(config.name)

        # Report unchanged configs (those that exist and are up to date)
        unchanged = [
            c.name
            for c in self.configs
            if c.name not in self.changes_made and c.name not in skipped_configs
        ]
        if unchanged:
            unchanged.sort()
            self.logger.info(
                "No changes needed for %d file%s:\n- %s",
                len(unchanged),
                "s" if len(unchanged) != 1 else "",
                "\n- ".join(unchanged),
            )

        # Report skipped configs separately
        if skipped_configs:
            skipped_configs.sort()
            self.logger.info(
                "Skipped %d file%s:\n- %s",
                len(skipped_configs),
                "s" if len(skipped_configs) != 1 else "",
                "\n- ".join(skipped_configs),
            )

    def fetch_remote_content(self, config: ConfigFile) -> str | None:
        """Fetch content from remote URL."""
        try:
            response = requests.get(config.url)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            self.logger.warning("Failed to download %s from remote.", config.name)
            return None

    def process_config(self, config: ConfigFile, remote_content: str) -> bool:
        """Process a single config file, updating or creating as needed.

        Returns:
            True if the config was updated or created, False otherwise.
        """
        # Check if this config falls under a rejected parent directory
        parent_dir = config.local_path.parent
        if any(str(parent_dir).startswith(str(rejected)) for rejected in self.skipped_dirs):
            self.logger.debug(
                "Skipping %s as parent directory %s was previously declined.",
                config.name,
                parent_dir,
            )
            return False

        if ("/" in config.name or "\\" in config.name) and not parent_dir.exists():
            if (
                self.no_confirm
                or self.should_create_all
                or confirm_action(
                    f"Directory {parent_dir} does not exist. Create?", default_to_yes=True
                )
            ):
                parent_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info("Created directory %s", parent_dir)
            else:
                self.logger.info(
                    "Skipping %s and all configs in %s as directory creation was declined.",
                    config.name,
                    parent_dir,
                )
                # Add this parent to rejected list to skip all future configs under it
                self.skipped_dirs.add(parent_dir)
                return False

        if config.local_path.exists():
            local_content = config.local_path.read_text()
            if local_content == remote_content:
                return False

            if not self.no_confirm:
                PolyDiff.content(local_content, remote_content, config.local_path.name)
                if not confirm_action(f"Update {config.name} config?", default_to_yes=True):
                    return False
        elif not (
            self.no_confirm
            or self.should_create_all
            or confirm_action(
                color(f"{config.name} config does not exist locally. Create?", "yellow"),
                default_to_yes=True,
            )
        ):
            return False

        # Write the file and log it
        config.local_path.write_text(remote_content)
        self.logger.info(
            "%s %s config from remote.",
            "Created" if not config.local_path.exists() else "Updated",
            config.name,
        )
        return True

    def run_post_update_command(self, config: ConfigFile) -> None:
        """Run post-update command for a config file."""
        if config.post_update_command is None:
            return

        try:
            cmd = config.post_update_command
            self.logger.info("Running post-update command for %s.", config.name)

            # Convert list to string if needed and run the command
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
            self.logger.debug("Executing: %s", cmd_str)
            subprocess.run(cmd_str, shell=True, check=True)

            self.logger.info("Post-update command for %s completed successfully!", config.name)

        except subprocess.CalledProcessError as e:
            self.logger.error(
                "Post-update command for %s failed. Exit code: %d.", config.name, e.returncode
            )
        except Exception as e:
            self.logger.error("Failed to run post-update command for %s: %s", config.name, str(e))


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = PolyArgs(description="Update config files from central repository")
    parser.add_argument("-y", action="store_true", help="update files without confirmation")
    parser.add_argument("--include-extras", action="store_true", help="include extra config files")
    return parser.parse_args()


def main() -> None:
    """Fetch and update the config files."""
    args = parse_args()

    manager = ConfigManager(include_extras=args.include_extras, no_confirm=args.y)
    manager.update_configs()


if __name__ == "__main__":
    main()
