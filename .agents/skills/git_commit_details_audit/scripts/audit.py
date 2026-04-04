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

def find_repo_for_sha(sha):
    """Search for the SHA in the main repo and submodules."""
    # Check main repo first
    if run_git(["rev-parse", "--quiet", "--verify", f"{sha}^{{commit}}"]):
        return ".", "Main Repository"
    
    # Check submodules
    submodules_raw = run_git(["submodule", "status", "--recursive"])
    if submodules_raw:
        for line in submodules_raw.splitlines():
            # Format:  <SHA> <Path> (<Branch>)
            parts = line.strip().split()
            if len(parts) >= 2:
                path = parts[1]
                if run_git(["rev-parse", "--quiet", "--verify", f"{sha}^{{commit}}"], cwd=path):
                    return path, f"Submodule: {path}"
    
    return None, None

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
