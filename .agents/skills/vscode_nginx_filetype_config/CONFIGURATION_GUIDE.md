# VSCode NGINX Configuration: Multi-Tier Setup Guide

This guide demonstrates how to configure VSCode to recognize NGINX files at three different tiers, depending on your needs.

***

## Overview

VSCode settings follow a hierarchy:

1. **Workspace** (`.vscode/settings.json`) — Project-specific, committed to repo, **highest priority**
2. **Profile** (`profiles/<name>/settings.json`) — Profile-specific, personal
3. **Application** (`User/settings.json`) — User-wide, affects all VSCode instances

This document shows how to configure NGINX file type recognition at each tier.

***

## Tier 1: Workspace Configuration (Recommended for Teams)

**Best for**: Team projects where all developers should have the same NGINX settings.

**Persistence**: Committed to repository, inherited by all team members.

### Manual Setup

```bash
# Navigate to repository root
cd /path/to/oleovista-acers

# Create .vscode directory
mkdir -p .vscode

# Create or edit .vscode/settings.json
cat > .vscode/settings.json << 'EOF'
{
  "files.associations": {
    "nginx/**": "nginx"
  }
}
EOF

# Commit to repository
git add .vscode/settings.json
git commit -m "feat: configure NGINX file type for workspace"
```

### Using Automation Script

```bash
cd /path/to/oleovista-acers
python3 /path/to/skill/scripts/vscode-nginx-config.py --tier workspace
```

### Verification

```bash
# Check workspace settings
cat .vscode/settings.json

# Or use jq
jq '.files.associations."nginx/**"' .vscode/settings.json
# Expected output: "nginx"
```

***

## Tier 2: Profile Configuration (For Personal Workflows)

**Best for**: Individual developers who want profile-specific settings without affecting team repo.

**Persistence**: Local to your machine, not shared.

**Prerequisites**: Profile must exist in VSCode. Create via:
- `Cmd+Shift+P` → "Profiles: Create Profile"

### Manual Setup

**macOS**:
```bash
# Create profile directory
mkdir -p ~/Library/Application\ Support/Code/User/profiles/my-profile

# Create or edit settings.json
cat > ~/Library/Application\ Support/Code/User/profiles/my-profile/settings.json << 'EOF'
{
  "files.associations": {
    "nginx/**": "nginx"
  }
}
EOF
```

**Linux**:
```bash
mkdir -p ~/.config/Code/User/profiles/my-profile
cat > ~/.config/Code/User/profiles/my-profile/settings.json << 'EOF'
{
  "files.associations": {
    "nginx/**": "nginx"
  }
}
EOF
```

**Windows (PowerShell)**:
```powershell
$ProfileDir = "$env:APPDATA\Code\User\profiles\my-profile"
New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null

$Settings = @{
    "files.associations" = @{
        "nginx/**" = "nginx"
    }
} | ConvertTo-Json

$Settings | Out-File -FilePath "$ProfileDir\settings.json" -Encoding UTF8
```

### Using Automation Script

```bash
python3 /path/to/skill/scripts/vscode-nginx-config.py \
  --tier profile \
  --profile-name my-profile
```

### Verification

**macOS**:
```bash
jq '.files.associations."nginx/**"' \
  ~/Library/Application\ Support/Code/User/profiles/my-profile/settings.json
# Expected output: "nginx"
```

Then activate the profile in VSCode and reload.

***

## Tier 3: Application Configuration (User-wide)

**Best for**: Individual developers who want NGINX settings across ALL VSCode projects.

**Persistence**: Local to your machine, affects all VSCode instances.

### Manual Setup

**macOS**:
```bash
# Create or edit application settings
mkdir -p ~/Library/Application\ Support/Code/User

# Merge into existing settings or create new
cat > ~/Library/Application\ Support/Code/User/settings.json << 'EOF'
{
  "files.associations": {
    "nginx/**": "nginx"
  }
}
EOF
```

**Linux**:
```bash
mkdir -p ~/.config/Code/User
cat > ~/.config/Code/User/settings.json << 'EOF'
{
  "files.associations": {
    "nginx/**": "nginx"
  }
}
EOF
```

**Windows (PowerShell)**:
```powershell
$AppDataPath = "$env:APPDATA\Code\User"
New-Item -ItemType Directory -Path $AppDataPath -Force | Out-Null

$Settings = @{
    "files.associations" = @{
        "nginx/**" = "nginx"
    }
} | ConvertTo-Json

$Settings | Out-File -FilePath "$AppDataPath\settings.json" -Encoding UTF8
```

### Using Automation Script

```bash
python3 /path/to/skill/scripts/vscode-nginx-config.py --tier application
```

### Verification

**macOS**:
```bash
jq '.files.associations."nginx/**"' \
  ~/Library/Application\ Support/Code/User/settings.json
# Expected output: "nginx"
```

Close and reopen VSCode to apply changes.

***

## Multi-Tier Configuration Strategy

### Recommended Approach

1. **Start with Application tier** for user-wide consistency:
   ```bash
   python3 vscode-nginx-config.py --tier application
   ```

2. **Add Workspace tier** for team projects (optional overrides):
   ```bash
   cd /path/to/project
   python3 vscode-nginx-config.py --tier workspace
   ```

3. **Add Profile tier** for personal workflows (optional):
   ```bash
   python3 vscode-nginx-config.py --tier profile --profile-name dev
   ```

### Priority When All Tiers Are Configured

Workspace > Profile > Application

This means if NGINX is defined at the workspace level, it overrides profile and application settings for that project.

***

## Verification Across All Tiers

```bash
# Verify application settings (macOS)
echo "=== Application ==="
jq '.files.associations."nginx/**"' ~/Library/Application\ Support/Code/User/settings.json 2>/dev/null || echo "Not configured"

# Verify profile settings (macOS)
echo "=== Profile (dev) ==="
jq '.files.associations."nginx/**"' ~/Library/Application\ Support/Code/User/profiles/dev/settings.json 2>/dev/null || echo "Not configured"

# Verify workspace settings
echo "=== Workspace ==="
jq '.files.associations."nginx/**"' .vscode/settings.json 2>/dev/null || echo "Not configured"
```

***

## Testing NGINX File Recognition

After configuring any tier:

1. **Open an NGINX file**:
   ```bash
   code nginx/nginx.conf
   ```

2. **Check language mode** (bottom-right of VSCode):
   - Should display `nginx` (not `plaintext`, `conf`, etc.)

3. **Verify syntax highlighting**:
   - Keywords like `server`, `location`, `proxy_pass` should be colored
   - Directives should be recognized

4. **If not working**:
   - Reload VSCode: `Cmd+Shift+P` → "Developer: Reload Window"
   - Or close and reopen VSCode

***

## Handling Existing Settings

All configuration methods use **atomic merge logic**:

- **Existing** `files.associations` entries are **preserved**
- **New** `nginx/**` entry is **added** without overwrites
- **No other settings** are modified

### Example

Before:
```json
{
  "python.linting.enabled": true,
  "files.associations": {
    "*.yaml": "yaml",
    "*.toml": "toml"
  }
}
```

After merge:
```json
{
  "python.linting.enabled": true,
  "files.associations": {
    "*.yaml": "yaml",
    "*.toml": "toml",
    "nginx/**": "nginx"
  }
}
```

***

## Troubleshooting

### NGINX files still show as plaintext

1. **Verify configuration was applied**:
   ```bash
   # Check all three tiers
   jq '.files.associations."nginx/**"' ~/.config/Code/User/settings.json
   jq '.files.associations."nginx/**"' ~/.config/Code/User/profiles/<profile>/settings.json
   jq '.files.associations."nginx/**"' .vscode/settings.json
   ```

2. **Reload VSCode**:
   ```
   Cmd+Shift+P → "Developer: Reload Window"
   ```

3. **Manually set language mode**:
   - Open NGINX file
   - Click language indicator (bottom-right)
   - Select `nginx` from dropdown

### No hierarchy precedence observed

Remember the priority order:
1. Workspace (highest)
2. Profile
3. Application (lowest)

If workspace defines `nginx/**`, it **overrides** all other tiers.

### Settings not persisting

Verify file locations and permissions:

```bash
# macOS examples
ls -la ~/Library/Application\ Support/Code/User/settings.json
ls -la ~/.vscode/settings.json
ls -la ~/Library/Application\ Support/Code/User/profiles/*/settings.json
```

If files don't exist, try creating them manually first, then re-running the script.

***

## Automation Script Reference

### Full Command Syntax

```bash
python3 vscode-nginx-config.py \
  [--tier {application|profile|workspace}] \
  [--workspace-root /path/to/project] \
  [--profile-name profile-name] \
  [--os {auto|macos|linux|windows}] \
  [--dry-run]
```

### Examples

```bash
# Workspace only
python3 vscode-nginx-config.py

# Application tier (user-wide)
python3 vscode-nginx-config.py --tier application

# Profile tier
python3 vscode-nginx-config.py --tier profile --profile-name dev

# Preview changes (dry run)
python3 vscode-nginx-config.py --tier workspace --dry-run

# Specific workspace root
python3 vscode-nginx-config.py --tier workspace --workspace-root /path/to/project

# Force OS detection (usually auto-detected)
python3 vscode-nginx-config.py --tier application --os windows
```

***

## Implementation for oleovista-acers

### Current Setup

The `oleovista-acers` repository now has workspace-level configuration:

```bash
# Location
.vscode/settings.json

# Content
{
  "files.associations": {
    "nginx/**": "nginx"
  }
}

# Git status
git log --oneline | grep nginx
# Should show: feat: configure VSCode NGINX file type for workspace
```

### For Individual Developers

To additionally configure at application or profile level:

```bash
# Application tier (affects all your VSCode projects)
cd /path/to/ai-suite/.agents/skills/vscode_nginx_filetype_config
python3 scripts/vscode-nginx-config.py --tier application

# Or profile tier (for specific workflow)
python3 scripts/vscode-nginx-config.py --tier profile --profile-name workspace-dev
```

***

## Related Resources

- **VSCode Settings**: https://code.visualstudio.com/docs/getstarted/settings
- **File Associations**: https://code.visualstudio.com/docs/languages/identifiers
- **NGINX IntelliSense Extension**: https://marketplace.visualstudio.com/items?itemName=hangxingliu.vscode-nginx-conf
- **Skill Documentation**: See `./SKILL.md` for full technical details
