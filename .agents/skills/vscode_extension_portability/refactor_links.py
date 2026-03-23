#!/usr/bin/env python3
"""
Refactor non-portable or temporary extension-linked paths in settings.json.
Targets Postman AI instruction files and absolute home directory prefixes.
"""

import json
import re
import os
import argparse
import shutil
from pathlib import Path

def refactor_path(path_str):
    """
    Apply portability logic to a single path string.
    - Replaces /var/folders/.../T/ with ~./antigravity/extensions/.../
    - Replaces /Users/<username>/ with ~/
    """
    if not isinstance(path_str, str):
        return path_str

    # 1. Handle Postman Temporary Cache (/var/folders/)
    # Regex targets the specific Postman agent-instructions-files structure
    postman_pattern = re.compile(r'/var/folders/[^/]+/[^/]+/T/postman.postman-for-vscode-[^/]+/agent-instructions-files/vscode/')
    if postman_pattern.search(path_str):
        # We replace the dynamic temp path with the stable extension path
        # Using a wildcard match for the version index to remain robust
        stable_base = "~/.antigravity/extensions/postman.postman-for-vscode-*/agent-instructions-files/vscode/"
        path_str = postman_pattern.sub(stable_base, path_str)

    # 2. Handle Absolute Home Directory (/Users/<username>/)
    home = str(Path.home())
    if path_str.startswith(home):
        path_str = path_str.replace(home, "~", 1)

    return path_str

def process_settings(file_path, dry_run=False):
    """Load, refactor, and save settings.json."""
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        print(f"Error: {file_path} not found.")
        return

    with open(path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {file_path}: {e}")
            return

    # Backup before modification
    if not dry_run:
        shutil.copy2(path, path.with_suffix('.json.bak'))
        print(f"Backup created at {path}.json.bak")

    # Target specific keys known to contain paths
    target_keys = [
        "chat.instructionsFilesLocations",
        "postman.ai.instructionsFilesLocations" # Hypothesized alternate key
    ]

    modified = False
    for key in target_keys:
        if key in data and isinstance(data[key], list):
            new_list = [refactor_path(p) for p in data[key]]
            if new_list != data[key]:
                data[key] = new_list
                modified = True
                print(f"Refactored paths in {key}")

    if modified:
        if dry_run:
            print("Dry run: Changes detected but not written.")
            print(json.dumps(data, indent=4))
        else:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
            print("Successfully updated settings.json with portable links.")
    else:
        print("No refactorable paths found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refactor VS Code settings for portability.")
    parser.add_argument("--file", required=True, help="Path to settings.json")
    parser.add_argument("--dry-run", action="store_true", help="Log changes without writing")
    args = parser.parse_args()

    process_settings(args.file, args.dry_run)
