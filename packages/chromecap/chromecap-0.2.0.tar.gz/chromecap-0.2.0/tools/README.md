# Chrome Cap Development Tools

This directory contains tools for developing and releasing Chrome Cap.

## Release Tool

The `release.py` script automates the process of bumping version numbers and creating GitHub releases.

### Usage

```bash
# Bump patch version (0.1.0 -> 0.1.1)
./tools/release.py patch

# Bump minor version (0.1.0 -> 0.2.0)
./tools/release.py minor

# Bump major version (0.1.0 -> 1.0.0)
./tools/release.py major

# Dry run (doesn't make any changes)
./tools/release.py patch --dry-run
```

### What It Does

1. Updates the version in `chromecap/__init__.py`
2. Updates the CHANGELOG.md file
3. Creates a git commit with the changes
4. Creates a git tag for the new version

After running the script, you need to push the changes to GitHub:

```bash
git push && git push --tags
``` 