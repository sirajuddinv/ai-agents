#!/usr/bin/env python3
"""
VSCode NGINX File Type Configuration Automation Utility

Automates the process of configuring VSCode to recognize NGINX files
across four tiers: application (user-wide), profile (profile-specific),
workspace (project-specific), and code-workspace (multi-root workspace file).

Merges file associations into settings.json without overwriting existing
settings. Supports all operating systems (macOS, Linux, Windows).

Usage:
    python3 vscode-nginx-config.py [--tier TIER] [options]

Tiers:
    application       Configure user-wide settings (affects all VSCode instances)
    profile           Configure profile-specific settings (requires --profile-name)
    workspace         Configure project-specific settings (default)
    code-workspace    Configure .code-workspace file (requires --workspace-file)

Flags:
    --tier {application|profile|workspace|code-workspace}: Configuration tier (default: workspace)
    --workspace-root PATH: Repository root path (default: current directory)
    --workspace-file PATH: Path to .code-workspace file (required if --tier code-workspace)
    --profile-name NAME: Profile name (required if --tier profile)
    --dry-run: Preview changes without modifying files
    --os {auto|macos|linux|windows}: OS detection (auto-detect by default)

Examples:
    # Configure workspace (project-level)
    python3 vscode-nginx-config.py --workspace-root /path/to/project

    # Configure application (user-wide)
    python3 vscode-nginx-config.py --tier application

    # Configure profile
    python3 vscode-nginx-config.py --tier profile --profile-name dev

    # Configure code-workspace file
    python3 vscode-nginx-config.py --tier code-workspace --workspace-file myproject.code-workspace

    # Preview changes
    python3 vscode-nginx-config.py --tier workspace --dry-run
"""

import json
import sys
import os
import platform
import copy
from pathlib import Path
from typing import Dict, Any


class VSCodeConfigManager:
    """Manages VSCode settings across multiple configuration tiers."""

    def __init__(self, tier: str = "workspace", workspace_root: str = ".", 
                 profile_name: str = "", workspace_file: str = "", os_type: str = "auto", dry_run: bool = False):
        self.tier = tier
        self.workspace_root = Path(workspace_root).resolve()
        self.profile_name = profile_name
        self.workspace_file = workspace_file
        self.os_type = self._detect_os(os_type)
        self.dry_run = dry_run
        self.settings_path = self._resolve_settings_path()

    def _detect_os(self, os_type: str) -> str:
        """Detect or validate operating system."""
        if os_type != "auto":
            return os_type
        
        system = platform.system()
        if system == "Darwin":
            return "macos"
        elif system == "Linux":
            return "linux"
        elif system == "Windows":
            return "windows"
        else:
            raise RuntimeError(f"Unsupported OS: {system}")

    def _resolve_settings_path(self) -> Path:
        """Resolve the settings.json path based on tier and OS."""
        if self.tier == "workspace":
            return self.workspace_root / ".vscode" / "settings.json"
        
        elif self.tier == "code-workspace":
            if not self.workspace_file:
                raise ValueError("--workspace-file is required for code-workspace tier")
            return Path(self.workspace_file).resolve()
        
        elif self.tier == "application":
            if self.os_type == "macos":
                base = Path.home() / "Library" / "Application Support" / "Code" / "User"
            elif self.os_type == "linux":
                base = Path.home() / ".config" / "Code" / "User"
            elif self.os_type == "windows":
                appdata = os.getenv("APPDATA")
                if not appdata:
                    raise RuntimeError("APPDATA environment variable not set")
                base = Path(appdata) / "Code" / "User"
            else:
                raise RuntimeError(f"Unknown OS: {self.os_type}")
            
            return base / "settings.json"
        
        elif self.tier == "profile":
            if not self.profile_name:
                raise ValueError("--profile-name is required for profile tier")
            
            if self.os_type == "macos":
                base = Path.home() / "Library" / "Application Support" / "Code" / "User"
            elif self.os_type == "linux":
                base = Path.home() / ".config" / "Code" / "User"
            elif self.os_type == "windows":
                appdata = os.getenv("APPDATA")
                if not appdata:
                    raise RuntimeError("APPDATA environment variable not set")
                base = Path(appdata) / "Code" / "User"
            else:
                raise RuntimeError(f"Unknown OS: {self.os_type}")
            
            return base / "profiles" / self.profile_name / "settings.json"
        
        else:
            raise ValueError(f"Unknown tier: {self.tier}")

    def _validate_json(self, file_path: Path) -> bool:
        """Verify file is valid JSON."""
        try:
            with open(file_path, 'r') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, IOError):
            return False

    def _read_settings(self) -> Dict[str, Any]:
        """Read existing settings.json or return empty dict."""
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"ERROR: {self.settings_path} contains invalid JSON", file=sys.stderr)
                sys.exit(1)
        return {}

    def _merge_nginx_association_standard(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Merge NGINX file association into standard settings (workspace, application, profile)."""
        if "files.associations" not in settings:
            settings["files.associations"] = {}
        
        settings["files.associations"]["nginx/**"] = "nginx"
        return settings

    def _merge_nginx_association_code_workspace(self, workspace: Dict[str, Any]) -> Dict[str, Any]:
        """Merge NGINX file association into code-workspace settings."""
        if "settings" not in workspace:
            workspace["settings"] = {}
        
        if "files.associations" not in workspace["settings"]:
            workspace["settings"]["files.associations"] = {}
        
        workspace["settings"]["files.associations"]["nginx/**"] = "nginx"
        return workspace

    def _write_settings(self, settings: Dict[str, Any]) -> None:
        """Write settings to file with proper formatting."""
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
            f.write('\n')  # Add trailing newline

    def _create_backup(self) -> None:
        """Create a backup of the settings file before modifications."""
        if self.settings_path.exists():
            backup_path = self.settings_path.with_suffix('.bak')
            with open(self.settings_path, 'r') as f:
                with open(backup_path, 'w') as bf:
                    bf.write(f.read())
            print(f"ℹ Backup created: {backup_path}")

    def execute(self) -> bool:
        """Execute the configuration merge."""
        print(f"Tier:           {self.tier}")
        print(f"Settings File:  {self.settings_path}")
        if self.tier == "profile":
            print(f"Profile Name:   {self.profile_name}")
        elif self.tier == "code-workspace":
            print(f"Workspace File: {self.workspace_file}")
        print(f"OS:             {self.os_type}")
        print(f"Dry Run:        {self.dry_run}")
        print()
        
        # Read existing settings
        print("Reading existing settings...")
        original_settings = self._read_settings()
        
        # Merge NGINX association based on tier
        print("Merging NGINX file association...")
        if self.tier == "code-workspace":
            updated_settings = self._merge_nginx_association_code_workspace(copy.deepcopy(original_settings))
        else:
            updated_settings = self._merge_nginx_association_standard(copy.deepcopy(original_settings))
        
        # Check if changes were made
        if original_settings == updated_settings:
            print("✓ NGINX association already present. No changes needed.")
            return True
        
        # Show preview
        print("\nPreview of changes:")
        print(json.dumps(updated_settings, indent=2))
        
        if self.dry_run:
            print("\n[DRY RUN] No files modified.")
            return True
        
        # Create backup
        self._create_backup()
        
        # Write settings
        print("\nWriting settings...")
        self._write_settings(updated_settings)
        
        # Validate output
        print("Validating output JSON...")
        if not self._validate_json(self.settings_path):
            print(f"ERROR: Failed to write valid JSON to {self.settings_path}", file=sys.stderr)
            sys.exit(1)
        
        print(f"✓ Successfully configured VSCode NGINX file type association.")
        if self.tier == "workspace":
            print(f"✓ Reload VSCode to apply changes (Cmd+Shift+P → 'Developer: Reload Window')")
        elif self.tier == "application":
            print(f"✓ Close and reopen VSCode to apply changes")
        elif self.tier == "profile":
            print(f"✓ Switch to profile '{self.profile_name}' and reload VSCode")
        elif self.tier == "code-workspace":
            print(f"✓ Open workspace from file and reload VSCode (File → Open Workspace from File)")
        
        return True


def parse_arguments():
    """Parse command-line arguments."""
    args = {
        'tier': 'workspace',
        'workspace_root': '.',
        'profile_name': '',
        'workspace_file': '',
        'os_type': 'auto',
        'dry_run': False
    }
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "--dry-run":
            args['dry_run'] = True
            i += 1
        elif arg == "--tier":
            if i + 1 < len(sys.argv):
                args['tier'] = sys.argv[i + 1]
                i += 2
            else:
                print("ERROR: --tier requires a value", file=sys.stderr)
                sys.exit(1)
        elif arg == "--workspace-root":
            if i + 1 < len(sys.argv):
                args['workspace_root'] = sys.argv[i + 1]
                i += 2
            else:
                print("ERROR: --workspace-root requires a value", file=sys.stderr)
                sys.exit(1)
        elif arg == "--workspace-file":
            if i + 1 < len(sys.argv):
                args['workspace_file'] = sys.argv[i + 1]
                i += 2
            else:
                print("ERROR: --workspace-file requires a value", file=sys.stderr)
                sys.exit(1)
        elif arg == "--profile-name":
            if i + 1 < len(sys.argv):
                args['profile_name'] = sys.argv[i + 1]
                i += 2
            else:
                print("ERROR: --profile-name requires a value", file=sys.stderr)
                sys.exit(1)
        elif arg == "--os":
            if i + 1 < len(sys.argv):
                args['os_type'] = sys.argv[i + 1]
                i += 2
            else:
                print("ERROR: --os requires a value", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"ERROR: Unknown argument: {arg}", file=sys.stderr)
            sys.exit(1)
    
    return args


def main():
    """Main entry point."""
    try:
        args = parse_arguments()
        manager = VSCodeConfigManager(**args)
        success = manager.execute()
        sys.exit(0 if success else 1)
    except (ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
