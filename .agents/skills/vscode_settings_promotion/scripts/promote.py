#!/usr/bin/env python3
"""
VS Code Settings Promotion Script (Industrial Grade)
Automates the migration of profile-specific settings to global scope with universal enforcement.
"""

import argparse
import json
import os
import shutil
import sys
from typing import List, Dict, Any

def load_json(path: str) -> Dict[str, Any]:
    """Load JSON file with error handling."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        sys.exit(1)

def save_json(path: str, data: Dict[str, Any], indent: int = 4) -> None:
    """Save JSON file with backup."""
    bak_path = f"{path}.bak"
    try:
        if os.path.exists(path):
            shutil.copy2(path, bak_path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent)
            f.write("\n")  # Final newline
    except Exception as e:
        print(f"Error saving {path}: {e}")
        sys.exit(1)

def promote_settings(
    profile_path: str, 
    global_path: str, 
    keys: List[str], 
    dry_run: bool = False
) -> None:
    """Promote settings from profile to global and append to applyToAllProfiles."""
    
    profile_data = load_json(profile_path)
    global_data = load_json(global_path)
    
    promoted = {}
    remaining_profile = profile_data.copy()
    
    for key in keys:
        if key in profile_data:
            promoted[key] = profile_data[key]
            if key in remaining_profile:
                del remaining_profile[key]
        else:
            print(f"Warning: Key '{key}' not found in profile configuration.")
    
    if not promoted:
        print("No settings were found to promote.")
        return

    # Update global data
    for key, value in promoted.items():
        global_data[key] = value

    # Update applyToAllProfiles
    apply_to_all = global_data.get("workbench.settings.applyToAllProfiles", [])
    for key in promoted.keys():
        if key not in apply_to_all:
            apply_to_all.append(key)
    
    # Ensure preservation of alphabetical order if user maintains it (optional, but industrial)
    # apply_to_all.sort() 
    
    global_data["workbench.settings.applyToAllProfiles"] = apply_to_all

    if dry_run:
        print("\n[DRY RUN] The following settings would be promoted:")
        print(json.dumps(promoted, indent=4))
        print("\n[DRY RUN] Keys added to applyToAllProfiles:")
        print(keys)
        return

    # Commit changes
    save_json(profile_path, remaining_profile)
    save_json(global_path, global_data)

    print(f"Successfully promoted {len(promoted)} settings to global scope.")
    print(f"Backups created at .bak locations.")

def main():
    parser = argparse.ArgumentParser(description="Promote VS Code settings to global scope.")
    parser.add_argument("--profile", required=True, help="Path to profile-specific settings.json")
    parser.add_argument("--global-settings", required=True, help="Path to global settings.json")
    parser.add_argument("--keys", nargs="+", required=True, help="Keys to promote")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without saving")
    
    args = parser.parse_args()
    
    promote_settings(args.profile, args.global_settings, args.keys, args.dry_run)

if __name__ == "__main__":
    main()
