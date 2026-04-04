import subprocess
import os
import sys
import re

def run_git(args, cwd=None):
    """Run a git command and return the output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            env={**os.environ, "PAGER": "cat"}
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_references_for_sha(sha, path):
    """Identify branches and tags containing the SHA, along with their current tips."""
    references = []
    
    # 1. Audit Branches
    branches_raw = run_git(["branch", "-a", "--contains", sha], cwd=path)
    if branches_raw:
        for line in branches_raw.splitlines():
            # Clean up the branch name (remove * and whitespace)
            branch = line.replace("*", "").strip()
            if branch:
                tip = run_git(["rev-parse", branch], cwd=path)
                references.append({
                    "type": "Branch",
                    "name": branch,
                    "tip": tip or "Unknown"
                })
    
    # 2. Audit Tags
    tags_raw = run_git(["tag", "--contains", sha], cwd=path)
    if tags_raw:
        for line in tags_raw.splitlines():
            tag = line.strip()
            if tag:
                tip = run_git(["rev-parse", tag], cwd=path)
                references.append({
                    "type": "Tag",
                    "name": tag,
                    "tip": tip or "Unknown"
                })
                
    return references

def format_commit_details(sha, path, repo_display_name):
    """Format the commit details into the required industrial template."""
    # Metadata: Author, Date, Full Message
    metadata = run_git([
        "show", "-s", 
        "--format=Author: %an <%ae>%nDate: %aD%nMessage: %B", 
        sha
    ], cwd=path)
    
    if not metadata:
        return "Error: Could not retrieve commit metadata."

    # Reference Audit (Branches & Tags)
    references = get_references_for_sha(sha, path)

    # Changed Files Inventory
    name_status = run_git(["show", "--name-status", "--format=", sha], cwd=path)
    
    # Full Hunks (Diffs)
    hunks = run_git(["show", "-p", "--format=", sha], cwd=path)

    # Repository name (folder basename)
    repo_name = os.path.basename(os.path.abspath(path))
    if path == ".":
        repo_name = os.path.basename(os.getcwd())

    output = []
    output.append(f"Repository: {repo_display_name}")
    output.append(f"Commit SHA: {sha}")
    
    # Split metadata into sections
    meta_lines = metadata.splitlines()
    author = meta_lines[0]
    date = meta_lines[1]
    message = "\n".join(meta_lines[2:]).replace("Message: ", "").strip()

    output.append(f"Commit Message: {message}")
    output.append(author)
    output.append(date)
    
    output.append("-" * 40)
    output.append("### REFERENCE AUDIT (Containing Branches & Tags)")
    if references:
        output.append(f"| Type | Name | Current Tip (HEAD) | Status |")
        output.append(f"| :--- | :--- | :--- | :--- |")
        for ref in references:
            status = "Diverged" if ref["tip"] != sha else "Current"
            output.append(f"| {ref['type']} | {ref['name']} | {ref['tip'][:8]} | {status} |")
    else:
        output.append("No active branches or tags contain this commit.")

    output.append("-" * 40)
    output.append("### CHANGED FILES INVENTORY")
    if name_status:
        output.append(name_status)
    else:
        output.append("No files modified (potential merge or empty commit).")
    
    output.append("-" * 40)
    output.append("### HUNK EXPOSURE (DIFFS)")
    if hunks:
        output.append(f"```diff\n{hunks}\n```")
    else:
        output.append("No hunks available.")

    return "\n".join(output)

def find_repo_for_sha(sha):
    """Find the repository (main or submodule) that contains the SHA."""
    # 1. Check main repository
    if run_git(["rev-parse", "--quiet", "--verify", f"{sha}^{{commit}}"]):
        return ".", "Main Repository (ai-suite)"
    
    # 2. Check submodules
    submodule_paths = []
    if os.path.exists(".gitmodules"):
        # Extract paths using git config to avoid manual parsing
        output = run_git(["config", "--file", ".gitmodules", "--get-regexp", "path"])
        if output:
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    submodule_paths.append(parts[1])
    
    for path in submodule_paths:
        if os.path.isdir(path):
            # Check if SHA exists in this submodule
            if run_git(["rev-parse", "--quiet", "--verify", f"{sha}^{{commit}}"], cwd=path):
                return path, f"Submodule ({path})"
                
    return None, None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 audit.py <COMMIT_SHA>")
        sys.exit(1)

    sha = sys.argv[1]
    path, display_name = find_repo_for_sha(sha)

    if not path:
        print(f"Error: Commit SHA '{sha}' not found in the main repository or any submodules.")
        sys.exit(1)

    print(format_commit_details(sha, path, display_name))

if __name__ == "__main__":
    main()
