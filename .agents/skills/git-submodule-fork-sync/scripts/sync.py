#!/usr/bin/env python3
import os
import subprocess
import json
import sys
import argparse

# Industrial Submodule Fork Sync Orchestrator (v1.1)

def run(cmd, shell=False, check=True):
    print(f"Executing: {cmd}")
    return subprocess.run(cmd, shell=shell, check=check, text=True, capture_output=True)

def get_gitmodules_mapping():
    if not os.path.exists(".gitmodules"): return []
    subs = {}
    current = None
    with open(".gitmodules", "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[submodule"):
                current = line.split("\"")[1]
                subs[current] = {}
            elif current and "=" in line:
                parts = line.split("=", 1)
                if len(parts) == 2:
                    subs[current][parts[0].strip()] = parts[1].strip()
    
    results = []
    for name, data in subs.items():
        path = data.get("path")
        if path:
            # Current origin
            origin = None
            if os.path.exists(os.path.join(path, ".git")):
                res = subprocess.run(["git", "-C", path, "remote", "get-url", "origin"], capture_output=True, text=True)
                if res.returncode == 0: origin = res.stdout.strip()
            
            # Historical original URL
            orig_url = None
            try:
                res = subprocess.run(["git", "log", "--reverse", "--format=%H", "-S", name, "--", ".gitmodules"], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    sha = res.stdout.strip().split("\n")[0]
                    res_content = subprocess.run(["git", "show", f"{sha}:.gitmodules"], capture_output=True, text=True)
                    import re
                    pattern = re.compile(rf"\[submodule \"{name}\"\]\s+path = .*?\s+url = (.*?)\s", re.DOTALL)
                    match = pattern.search(res_content.stdout)
                    if match: orig_url = match.group(1).strip()
            except: pass
            
            results.append({
                "name": name,
                "path": path,
                "current_origin": origin,
                "original_url": orig_url,
                "is_fork": (origin and orig_url and "Baneeishaque" in origin and "Baneeishaque" not in orig_url)
            })
    return results

def cmd_analyze(args):
    mapping = get_gitmodules_mapping()
    discrepancies = [s for s in mapping if s["is_fork"]]
    if not discrepancies:
        print("No fork discrepancies detected.")
        return
    print(f"Detected {len(discrepancies)} forked submodules requiring alignment:")
    for d in discrepancies:
        print(f" - {d['name']}: {d['original_url']} -> {d['current_origin']}")

def cmd_rebuild(args):
    """Executes the Total History Reconstruction Strategy."""
    mapping = get_gitmodules_mapping()
    if not args.base:
        print("Error: --base SHA required for reconstruction.")
        sys.exit(1)
        
    print(f"WARNING: This will reset HEAD to {args.base} and rebuild {len(mapping)} commits.")
    if not args.force:
        confirm = input("Are you sure? (y/N): ")
        if confirm.lower() != "y": return

    # 1. Reset
    run(["git", "reset", "--hard", args.base])
    run("rm -rf .git/modules/*", shell=True)
    
    # 2. Purge paths
    for sub in mapping:
        if os.path.exists(sub["path"]):
            import shutil
            shutil.rmtree(sub["path"])
            
    # 3. rebuild loop
    if not os.path.exists(".gitmodules"):
        with open(".gitmodules", "w") as f: f.write("")
        run(["git", "add", ".gitmodules"])

    for sub in mapping:
        url = sub["current_origin"] if sub["is_fork"] else sub["original_url"]
        run(["git", "submodule", "add", url, sub["path"]])
        if sub["is_fork"]:
            run(["git", "-C", sub["path"], "remote", "add", "upstream", sub["original_url"]])
        run(["git", "commit", "-m", f"chore(submodules): add {sub['name']}"])

    print("\nReconstruction successful. Feature commits must now be cherry-picked on top.")

def main():
    parser = argparse.ArgumentParser(description="Git Submodule Fork Sync Orchestrator")
    subparsers = parser.add_subparsers()
    
    p_analyze = subparsers.add_parser("analyze")
    p_analyze.set_defaults(func=cmd_analyze)
    
    p_rebuild = subparsers.add_parser("rebuild")
    p_rebuild.add_argument("--base", required=True, help="Base commit SHA to rebuild from")
    p_rebuild.add_argument("--force", action="store_true", help="Skip confirmation")
    p_rebuild.set_defaults(func=cmd_rebuild)
    
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
