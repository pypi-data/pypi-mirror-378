#!/usr/bin/env python3
"""Release script for Chrome Cap.

This script automates the process of bumping version numbers
and creating GitHub releases.
"""
import argparse
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_current_version():
    """Get the current version from __init__.py."""
    init_path = PROJECT_ROOT / "chromecap" / "__init__.py"
    with open(init_path, "r") as f:
        content = f.read()
    
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not version_match:
        raise ValueError("Could not find version in __init__.py")
    
    return version_match.group(1)


def bump_version(current_version, bump_type):
    """Bump the version number based on the bump type."""
    major, minor, patch = map(int, current_version.split("."))
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_init_file(new_version):
    """Update the version in __init__.py."""
    init_path = PROJECT_ROOT / "chromecap" / "__init__.py"
    with open(init_path, "r") as f:
        content = f.read()
    
    new_content = re.sub(
        r'__version__\s*=\s*["\']([^"\']+)["\']',
        f'__version__ = "{new_version}"',
        content
    )
    
    with open(init_path, "w") as f:
        f.write(new_content)


def update_changelog(new_version, bump_type):
    """Update the CHANGELOG.md file."""
    changelog_path = PROJECT_ROOT / "CHANGELOG.md"
    with open(changelog_path, "r") as f:
        content = f.read()
    
    today = datetime.now().strftime("%Y-%m-%d")
    unreleased_section = re.search(r'## \[Unreleased\](.*?)(?=##|\Z)', content, re.DOTALL)
    
    if not unreleased_section:
        raise ValueError("Could not find Unreleased section in CHANGELOG.md")
    
    unreleased_content = unreleased_section.group(1).strip()
    
    # Replace the Unreleased section with the new version
    new_content = content.replace(
        f"## [Unreleased]{unreleased_content}",
        f"## [Unreleased]\n\n### Added\n- \n\n### Changed\n- \n\n### Fixed\n- \n\n## [{new_version}] - {today}{unreleased_content}"
    )
    
    with open(changelog_path, "w") as f:
        f.write(new_content)


def create_git_tag(new_version):
    """Create a Git tag for the new version."""
    tag_name = f"v{new_version}"
    message = f"Release {tag_name}"
    
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "tag", "-a", tag_name, "-m", message], check=True)
    
    print(f"Git tag {tag_name} created.")
    print("Run 'git push && git push --tags' to push the changes to GitHub.")


def main():
    parser = argparse.ArgumentParser(description="Release script for Chrome Cap")
    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch"],
        help="Type of version bump (major, minor, patch)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    current_version = get_current_version()
    new_version = bump_version(current_version, args.bump_type)
    
    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")
    
    if args.dry_run:
        print("Dry run. No changes made.")
        return
    
    update_init_file(new_version)
    print(f"Updated version in __init__.py to {new_version}")
    
    update_changelog(new_version, args.bump_type)
    print("Updated CHANGELOG.md")
    
    create_git_tag(new_version)


if __name__ == "__main__":
    main() 