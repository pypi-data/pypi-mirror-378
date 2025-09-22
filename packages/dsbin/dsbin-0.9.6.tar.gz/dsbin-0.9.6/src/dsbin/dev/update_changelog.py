"""Update CHANGELOG.md with a new version and automatically manage links."""

from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING

from polykit import PolyArgs, PolyLog

if TYPE_CHECKING:
    import argparse
    from collections.abc import Sequence
    from urllib.parse import ParseResult

logger = PolyLog.get_logger()

GITHUB_USERNAME = "dannystewart"
CHANGELOG_PATH = Path("CHANGELOG.md")


def _extract_repo_from_ssh_url(url: str) -> str | None:
    """Extract repository name from SSH format Git URL."""
    logger.debug("Parsing SSH URL: %s", url)
    path_parts = url.split(":", maxsplit=1)[-1].split("/")
    logger.debug("Path parts after split: %s", path_parts)

    if len(path_parts) >= 2:
        username = path_parts[-2]
        repo_name = path_parts[-1].rstrip(".git")
        logger.debug("Extracted username: %s, repo_name: %s", username, repo_name)

        # Verify this is actually your repo
        if username != GITHUB_USERNAME:
            logger.warning("Git remote points to %s/%s, not your repo.", username, repo_name)
            return None
        logger.debug("Username matches, returning repo_name: %s", repo_name)
        return repo_name

    logger.debug("Not enough path parts, returning None.")
    return None


def _extract_repo_from_https_url(parsed_url: ParseResult) -> str | None:
    """Extract repository name from HTTPS format Git URL."""
    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) >= 2:
        username = path_parts[0]
        repo_name = path_parts[1].rstrip(".git")

        # Verify this is actually your repo
        if username != GITHUB_USERNAME:
            logger.warning("Git remote points to %s/%s, not your repo.", username, repo_name)
            return None
        return repo_name
    return None


def _verify_repo_exists(repo_name: str) -> bool:
    """Verify the repository exists by checking with gh CLI."""
    try:
        subprocess.run(
            ["gh", "repo", "view", f"{GITHUB_USERNAME}/{repo_name}", "--json", "name"],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_repo_url(repo_override: str | None = None) -> str:
    """Get the GitHub repository URL.

    Raises:
        ValueError: If repository auto-detection fails and no override is provided.
    """
    if repo_override:
        return f"https://github.com/{GITHUB_USERNAME}/{repo_override}"

    # Try to get repo name from Git remote
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True,
        )
        url = result.stdout.strip()
        logger.debug("Got Git remote URL: %s", url)

        # Extract repo name from URL
        from urllib.parse import urlparse

        repo_name = None
        parsed_url = urlparse(url)
        logger.debug("Parsed URL hostname: %s", parsed_url.hostname)

        # Check for SSH URLs first (urlparse doesn't handle them properly)
        if url.startswith("git@github.com:"):
            logger.debug("Using SSH URL parser.")
            repo_name = _extract_repo_from_ssh_url(url)
        elif parsed_url.hostname == "github.com":
            logger.debug("Hostname matches github.com.")
            logger.debug("Using HTTPS URL parser.")
            repo_name = _extract_repo_from_https_url(parsed_url)
        else:
            logger.debug("Hostname does not match github.com.")

        logger.debug("Final repo_name result: %s", repo_name)

        if repo_name:
            constructed_url = f"https://github.com/{GITHUB_USERNAME}/{repo_name}"

            # Verify the repository exists
            if _verify_repo_exists(repo_name):
                logger.debug("Verified repository: %s", constructed_url)
                return constructed_url
            logger.warning("Could not verify repository exists: %s", constructed_url)

        logger.warning("Could not extract valid repository name from Git remote.")

    except subprocess.CalledProcessError:
        logger.warning("Failed to get Git remote URL.")

    # If we get here, auto-detection failed
    error_msg = "Repository auto-detection failed. Please specify --repo manually."

    raise ValueError(error_msg)


def get_latest_version() -> str:
    """Get the latest version from pyproject.toml.

    Raises:
        ValueError: If the version is not found in pyproject.toml.
    """
    try:
        with Path("pyproject.toml").open(encoding="utf-8") as f:
            for line in f:
                if match := re.search(r'version\s*=\s*["\']([^"\']+)["\']', line):
                    return match.group(1)
        msg = "Version not found in pyproject.toml"
        raise ValueError(msg)
    except Exception as e:
        logger.error("Failed to get version from pyproject.toml: %s", str(e))
        raise


def get_previous_version() -> str:
    """Get the previous version from the changelog."""
    try:
        content = CHANGELOG_PATH.read_text(encoding="utf-8")
        # Look for all version headers
        versions = re.findall(r"## \[(\d+\.\d+\.\d+)\]", content)

        if not versions:
            logger.debug("No versions found in changelog.")
            return "0.0.0"  # Fallback if no versions found

        logger.debug("Found versions in changelog: %s", versions)
        return versions[0]  # Return the most recent version
    except Exception as e:
        logger.debug("Error reading changelog: %s", str(e))
        return "0.0.0"


def create_version_entry(version: str, sections: dict[str, list[str]]) -> str:
    """Create a new version entry for the changelog."""
    today = time.strftime("%Y-%m-%d")
    entry = f"## [{version}] ({today})\n\n"

    for section, items in sections.items():
        if items:
            entry += f"### {section}\n"
            for item in items:
                entry += f"- {item}\n"
            entry += "\n"

    return entry


def create_new_changelog(version: str, new_entry: str, repo_url: str) -> str:
    """Create a new changelog file with the given version entry."""
    return f"""# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [Unreleased]

{new_entry}
<!-- Links -->
[Keep a Changelog]: https://keepachangelog.com/en/1.1.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html

<!-- Versions -->
[unreleased]: {repo_url}/compare/v{version}...HEAD
[{version}]: {repo_url}/releases/tag/v{version}
"""


def insert_version_into_changelog(content: str, new_entry: str, version: str) -> str:
    """Insert a new version entry into an existing changelog, maintaining version order."""
    from packaging import version as pkg_version

    # Find the Unreleased section
    unreleased_match = re.search(r"## \[Unreleased\].*?\n(?:\n|$)", content, re.IGNORECASE)

    # When adding a new version, check if there's content in the Unreleased section
    # If there is, insert the new version entry right after the Unreleased header
    if unreleased_match:
        unreleased_content_match = re.search(
            r"## \[Unreleased\].*?\n\n(.*?)(?=\n## |\Z)", content, re.DOTALL
        )
        if unreleased_content_match and unreleased_content_match.group(1).strip():
            # There's content in the Unreleased section, insert after the header
            pos = unreleased_match.end()
            return f"{content[:pos]}{new_entry}{content[pos:]}"

    # If no Unreleased section with content, proceed with normal version ordering
    # Extract all existing version headers
    version_matches = list(re.finditer(r"## \[(\d+\.\d+\.\d+)\]", content))
    existing_versions = [(m.group(1), m.start()) for m in version_matches]

    # If no versions exist yet
    if not existing_versions:
        if unreleased_match:
            # Insert after the Unreleased section
            pos = unreleased_match.end()
            return f"{content[:pos]}{new_entry}{content[pos:]}"

        # No Unreleased section either, insert at the beginning or after intro
        parts = content.split("\n\n", 2)
        if len(parts) >= 2:
            return f"{parts[0]}\n\n{parts[1]}\n\n{new_entry}{parts[2] if len(parts) > 2 else ''}"
        return f"{content}\n\n{new_entry}"

    # Sort existing versions
    version_obj = pkg_version.parse(version)

    # Find the position to insert the new version
    insert_pos = None

    for existing_ver, pos in existing_versions:
        existing_ver_obj = pkg_version.parse(existing_ver)
        if version_obj > existing_ver_obj:
            insert_pos = pos
            break

    if insert_pos is not None:
        # Insert before the first version that's smaller than the new version
        return f"{content[:insert_pos]}{new_entry}{content[insert_pos:]}"

    # If the new version is smaller than all existing versions, add it at the end
    # Find the end of the last version section
    last_version_pos = existing_versions[-1][1]

    # Find the next section after the last version (if any)
    next_section_match = re.search(r"^#", content[last_version_pos:], re.MULTILINE)
    if next_section_match:
        insert_pos = last_version_pos + next_section_match.start()
    else:
        # No next section, insert at the end or before the links section
        links_section = re.search(r"<!-- Links -->", content)
        insert_pos = links_section.start() if links_section else len(content)

    return f"{content[:insert_pos]}{new_entry}{content[insert_pos:]}"


def update_version_links(content: str, version: str, repo_url: str) -> str:
    """Update the version links section in the changelog."""
    from packaging import version as pkg_version

    # Extract all existing version links
    links = {}
    for match in re.finditer(r"\[([\d\.]+)\]: (.*)", content):
        ver, url = match.groups()
        links[ver] = url

    # Add the new version if it doesn't exist
    if version not in links:
        # Default link will be updated later
        links[version] = ""

    # Get all versions and sort them
    versions = [v for v in links if v != "unreleased"]
    versions_sorted = sorted(versions, key=pkg_version.parse, reverse=True)

    # Regenerate comparison links for all versions to ensure consistency
    for i, ver in enumerate(versions_sorted):
        # Skip the last version as it has no previous version to compare with
        if i == len(versions_sorted) - 1:
            # For the oldest version, use the release tag URL
            links[ver] = f"{repo_url}/releases/tag/v{ver}"
            continue

        next_ver = versions_sorted[i + 1]

        # Only regenerate URLs that follow the standard comparison pattern
        # This preserves any custom URLs that don't match the pattern
        current_url = links[ver]
        standard_pattern = f"{repo_url}/compare/v"

        # If URL doesn't exist or matches standard pattern, regenerate it
        if not current_url or current_url.startswith(standard_pattern):
            links[ver] = f"{repo_url}/compare/v{next_ver}...v{ver}"

    # Update unreleased link to point to the highest version
    if versions_sorted:
        highest_version = versions_sorted[0]
        links["unreleased"] = f"{repo_url}/compare/v{highest_version}...HEAD"
    else:
        links["unreleased"] = f"{repo_url}/compare/main...HEAD"

    # Build the new versions section
    new_links_section = "<!-- Versions -->\n"
    new_links_section += f"[unreleased]: {links['unreleased']}\n"
    for ver in versions_sorted:
        new_links_section += f"[{ver}]: {links[ver]}\n"

    # Replace the entire versions section
    if "<!-- Versions -->" in content:
        content = re.sub(
            r"<!-- Versions -->.*?(\n\n|$)",
            new_links_section + "\n",
            content,
            flags=re.DOTALL,
        )
    else:
        # Add Versions section if it doesn't exist
        content += f"\n{new_links_section}\n"

    return content


def update_changelog(version: str, sections: dict[str, list[str]], repo_url: str) -> None:
    """Update the changelog with a new version entry and update all links."""
    try:
        new_entry = create_version_entry(version, sections)

        if not CHANGELOG_PATH.exists():
            # Create a new changelog if it doesn't exist
            content = create_new_changelog(version, new_entry, repo_url)
            CHANGELOG_PATH.write_text(content, encoding="utf-8")
            logger.info("Created new changelog with version %s.", version)

        # Update existing changelog
        content = CHANGELOG_PATH.read_text(encoding="utf-8")

        # Check if version already exists
        if re.search(rf"## \[{re.escape(version)}\]", content):
            logger.info("Version %s already exists in changelog, skipping entry creation.", version)
            section_exists = True
        else:
            logger.info("Adding version %s to changelog.", version)
            content = insert_version_into_changelog(content, new_entry, version)
            section_exists = False

        # Update version links
        content = update_version_links(content, version, repo_url)

        # Ensure exactly one blank line at the end of the file
        content = content.rstrip("\n") + "\n"

        CHANGELOG_PATH.write_text(content, encoding="utf-8")

        if not section_exists:
            logger.info("Updated changelog with version %s.", version)

    except Exception as e:
        logger.error("Failed to update changelog: %s", str(e))
        raise


def find_previous_version(version: str) -> str:
    """Find the previous version in the changelog.

    Args:
        version: The current version.

    Returns:
        The previous version, or "0.0.0" if none found.
    """
    try:
        changelog_content = CHANGELOG_PATH.read_text(encoding="utf-8")
        versions = re.findall(r"## \[(\d+\.\d+\.\d+)\]", changelog_content)

        if len(versions) > 1:
            # Find the version that comes after the current one in the list
            for i, ver in enumerate(versions):
                if ver == version and i + 1 < len(versions):
                    prev_version = versions[i + 1]
                    logger.debug("Found previous version: %s (current: %s).", prev_version, version)
                    return prev_version

        logger.debug("No previous version found for %s.", version)
        return "0.0.0"
    except Exception as e:
        logger.error("Error finding previous version: %s", str(e))
        return "0.0.0"


def extract_version_content(version: str) -> str | None:
    """Extract the content for a specific version from the changelog.

    Args:
        version: The version to extract content for.

    Returns:
        The extracted content, or None if not found.
    """
    try:
        content = CHANGELOG_PATH.read_text(encoding="utf-8")
        version_pattern = rf"## \[{re.escape(version)}\].*?\n\n(.*?)(?=\n## |\Z)"
        match = re.search(version_pattern, content, re.DOTALL)

        if not match:
            logger.error("Failed to extract content for version %s from changelog.", version)
            return None

        return match.group(1).strip()
    except Exception as e:
        logger.error("Failed to extract version content: %s", str(e))
        return None


def add_or_update_changelog_link(
    content: str, version: str, prev_version: str, repo_url: str
) -> str:
    """Add or update the Full Changelog link in the content.

    Args:
        content: The release notes content.
        version: The current version.
        prev_version: The previous version.
        repo_url: The repository URL.

    Returns:
        The content with the changelog link added or updated.
    """
    # Check if we have a valid previous version
    if prev_version == "0.0.0":
        logger.debug("Skipping changelog link: no previous version found.")
        return content

    # Prepare the changelog link
    changelog_link = f"**Full Changelog:** {repo_url}/compare/v{prev_version}...v{version}"

    # Check if the content already has a Full Changelog link
    if "Full Changelog:" not in content:
        # Add the link with proper spacing
        if not content.endswith("\n\n"):
            if content.endswith("\n"):
                content += "\n"
            else:
                content += "\n\n"

        logger.debug("Adding changelog link: %s", changelog_link)
        return content + changelog_link
    # Update the existing link
    updated_content = re.sub(
        r"(?:\*\*)?Full Changelog:(?:\*\*)? .*",
        changelog_link,
        content,
    )
    logger.debug("Updated existing changelog link.")
    return updated_content


def check_release_exists(tag: str) -> bool:
    """Check if a GitHub release with the given tag exists.

    Args:
        tag: The tag to check.

    Returns:
        True if the release exists, False otherwise.
    """
    try:
        result = subprocess.run(
            ["gh", "release", "view", tag], check=False, capture_output=True, text=True
        )
        return result.returncode == 0
    except subprocess.SubprocessError:
        logger.error("Failed to check if release exists.")
        return False


def execute_gh_command(cmd: list[str]) -> bool:
    """Execute a GitHub CLI command."""
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error("GitHub CLI command failed: %s", e.stderr)
        return False


def get_changelog_versions() -> list[tuple[str, str]]:
    """Extract all versions and their content from the changelog.

    Returns:
        List of (version, content) tuples.
    """
    if not CHANGELOG_PATH.exists():
        logger.error("Changelog file not found.")
        return []

    try:
        changelog_content = CHANGELOG_PATH.read_text(encoding="utf-8")

        # Extract all versions from the changelog
        version_pattern = r"## \[(\d+\.\d+\.\d+)\].*?\n\n(.*?)(?=\n## |\Z)"
        version_matches = re.finditer(version_pattern, changelog_content, re.DOTALL)

        versions = []
        for match in version_matches:
            version = match.group(1)
            content = match.group(2).strip()
            versions.append((version, content))

        logger.info("Found %d versions in changelog.", len(versions))
        return versions
    except Exception as e:
        logger.error("Failed to extract versions from changelog: %s", str(e))
        return []


def get_release_notes(tag: str) -> str | None:
    """Get the release notes for a GitHub release.

    Args:
        tag: The release tag.

    Returns:
        The release notes, or None if the release doesn't exist or an error occurred.
    """
    try:
        result = subprocess.run(
            ["gh", "release", "view", tag, "--json", "body"],
            capture_output=True,
            text=True,
            check=True,
        )
        import json

        release_data = json.loads(result.stdout)
        return release_data.get("body", "")
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        logger.error("Failed to get release notes for %s: %s", tag, str(e))
        return None


def update_single_release(version: str, content: str, repo_url: str, dry_run: bool = False) -> bool:
    """Check and update a single GitHub release.

    Args:
        version: The version number.
        content: The changelog content for this version.
        repo_url: The repository URL.
        dry_run: If True, only report issues without making changes.

    Returns:
        True if the release was updated or is up to date, False on error.
    """
    tag = f"v{version}"

    # Check if release exists
    if not check_release_exists(tag):
        logger.info("GitHub release %s does not exist, skipping.", tag)
        return False

    # Get current release notes
    current_notes = get_release_notes(tag)
    if current_notes is None:
        return False

    # Find the previous version for the changelog link
    prev_version = find_previous_version(version)

    # Format the changelog content with the link
    formatted_content = add_or_update_changelog_link(content, version, prev_version, repo_url)

    # Compare and update if different
    if current_notes.strip() != formatted_content.strip():
        logger.info("GitHub release %s needs updating.", tag)

        if dry_run:
            return True

        cmd = ["gh", "release", "edit", tag, "--notes", formatted_content]
        if execute_gh_command(cmd):
            logger.info("Successfully updated GitHub release %s.", tag)
            return True
        logger.error("Failed to update GitHub release %s.", tag)
        return False
    logger.info("GitHub release %s is up to date.", tag)
    return True


def verify_release(version: str, content: str, repo_url: str, dry_run: bool) -> tuple[bool, bool]:
    """Check if a release needs updating and update it if needed.

    Args:
        version: The version number.
        content: The changelog content.
        repo_url: The repository URL.
        dry_run: If True, don't actually update.

    Returns:
        Tuple of (needs_update, was_updated).
    """
    tag = f"v{version}"

    # Check if release exists
    if not check_release_exists(tag):
        logger.info("GitHub release %s does not exist, skipping.", tag)
        return False, False

    # Get current release notes
    current_notes = get_release_notes(tag)
    if current_notes is None:
        return False, False

    # Find the previous version for the changelog link
    prev_version = find_previous_version(version)

    # Format the changelog content with the link
    formatted_content = add_or_update_changelog_link(content, version, prev_version, repo_url)

    # Compare and see if update is needed
    needs_update = current_notes.strip() != formatted_content.strip()
    was_updated = False

    if needs_update:
        logger.info("GitHub release %s needs updating.", tag)

        if not dry_run:
            cmd = ["gh", "release", "edit", tag, "--notes", formatted_content]
            if execute_gh_command(cmd):
                was_updated = True
                logger.info("Successfully updated GitHub release %s.", tag)
            else:
                logger.error("Failed to update GitHub release %s.", tag)
    else:
        logger.info("GitHub release %s is up to date.", tag)

    return needs_update, was_updated


def match_releases_to_changelog(repo_url: str, dry_run: bool = False) -> int:
    """Verify and match all GitHub release text with changelog content.

    Args:
        repo_url: The repository URL.
        dry_run: If True, only report issues without making changes.

    Returns:
        Number of releases that were updated.
    """
    # Get all versions from the changelog
    versions = get_changelog_versions()
    if not versions:
        return 0

    # Track updates
    updates_needed = 0
    updates_made = 0

    # Process each version
    for version, content in versions:
        needs_update, was_updated = verify_release(version, content, repo_url, dry_run)

        if needs_update:
            updates_needed += 1

        if was_updated:
            updates_made += 1

    # Report results
    if dry_run and updates_needed > 0:
        logger.info(
            "%d GitHub releases need updating. Run without --dry-run to apply changes.",
            updates_needed,
        )
    elif updates_needed == 0:
        logger.info("All GitHub releases are up to date with the changelog.")
    else:
        logger.info("Updated %d GitHub releases to match the changelog.", updates_made)

    return updates_made


def update_release_content(
    version: str, content: str, repo_url: str, dry_run: bool = False
) -> bool:
    """Update a GitHub release with content from the changelog.

    Args:
        version: The version for the release (e.g., '1.2.3')
        content: The content for the release notes.
        repo_url: The GitHub repository URL.
        dry_run: If True, print what would be done without making any changes.

    Returns:
        True if successful, False otherwise.
    """
    tag = f"v{version}"

    # Find the previous version
    prev_version = find_previous_version(version)

    # Add or update the changelog link
    formatted_content = add_or_update_changelog_link(content, version, prev_version, repo_url)

    # Check if release exists
    release_exists = check_release_exists(tag)

    if not release_exists:
        logger.error(
            "GitHub release %s does not exist. Please create the release on GitHub first.", tag
        )
        return False

    if dry_run:
        logger.info("Would update GitHub release %s with the following content:", tag)
        print("\n" + formatted_content)
        return True

    # Update the release
    logger.info("Updating GitHub release %s.", tag)
    cmd = ["gh", "release", "edit", tag, "--notes", formatted_content]

    success = execute_gh_command(cmd)

    if success:
        logger.info("Successfully updated GitHub release %s.", tag)

    return success


def update_release_on_github(version: str, repo_url: str, dry_run: bool) -> bool:
    """Update a GitHub release with content from the changelog.

    Args:
        version: The version to update.
        repo_url: The repository URL.
        dry_run: Whether to perform a dry run.

    Returns:
        True if successful, False otherwise.
    """
    if version_content := extract_version_content(version):
        return update_release_content(version, version_content, repo_url, dry_run=dry_run)
    logger.error("Could not find version %s in the changelog.", version)
    return False


def verify_gh_cli() -> bool:
    """Verify that GitHub CLI is installed and authenticated."""
    try:
        # Check if gh is installed
        subprocess.run(["gh", "--version"], check=True, capture_output=True)

        # Check if authenticated
        result = subprocess.run(
            ["gh", "auth", "status"],
            check=False,  # Don't fail if not authenticated
            capture_output=True,
            text=True,
        )

        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = PolyArgs(description=__doc__, add_version=False)
    parser.add_argument(
        "--add",
        "-a",
        help="version to add (defaults to version from pyproject.toml)",
    )
    parser.add_argument(
        "--repo-name",
        "-r",
        help="GitHub repo name to use for links (defaults to auto-detect)",
    )
    parser.add_argument(
        "--update",
        "-u",
        nargs="?",
        const=True,
        metavar="VERSION",
        help="update a single release with changelog content (defaults to current version)",
    )
    parser.add_argument(
        "--update-all",
        action="store_true",
        help="update all existing releases based on changelog content",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print what would be done without making any changes",
    )
    return parser.parse_args(args)


def main() -> int:
    """Update the changelog with a new version."""
    args = parse_args()

    try:
        # Get repo URL
        repo_url = get_repo_url(args.repo_name)

        # Check if GitHub CLI is needed and available
        if (args.update_all or args.update) and not verify_gh_cli():
            logger.error(
                "GitHub CLI (gh) not found or not authenticated. "
                "Please install and authenticate with 'gh auth login'."
            )
            return 1

        # Handle updating all GitHub releases
        if args.update_all:
            match_releases_to_changelog(repo_url, dry_run=args.dry_run)
            return 0

        # Handle updating a single GitHub release without modifying the changelog
        if args.update and isinstance(args.update, str):
            return 0 if update_release_on_github(args.update, repo_url, args.dry_run) else 1

        # Get the version to add to changelog
        version = args.add or get_latest_version()

        # Empty sections for manual editing
        sections = {"Added": [], "Changed": [], "Fixed": []}

        # Update the changelog
        update_changelog(version, sections, repo_url)

        # Update GitHub release for current version if requested
        if args.update and not update_release_on_github(version, repo_url, args.dry_run):
            return 1

        return 0
    except Exception as e:
        logger.error("Failed to update changelog: %s", str(e))
        return 1


if __name__ == "__main__":
    main()
