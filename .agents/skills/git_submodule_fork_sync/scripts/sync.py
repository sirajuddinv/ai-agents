#!/usr/bin/env python3
import os
import subprocess
import sys

def get_gitmodules_urls():
    if not os.path.exists(".gitmodules"): return {}
    urls = {}
    current_sub = None
    with open(".gitmodules", "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[submodule"):
                current_sub = line.split("\"")[1]
            elif line.startswith("url =") and current_sub:
                urls[current_sub] = line.split("=", 1)[1].strip()
    return urls

def get_origin_commit_for_submodule(sub):
    res = subprocess.run(["git", "log", "--reverse", "--format=%H", "-S", sub, "--", ".gitmodules"], capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        return res.stdout.strip().split("\n")[0][:7] # Use short SHA for reliability in sequences
    return None

def sequence_editor_mode(filepath):
    # This mode is called by git rebase to rewrite the git-rebase-todo file
    mapping_str = os.environ.get("SYNC_MAPPINGS", "")
    if not mapping_str: return
    
    # parse mappings: "sha1:sub1:url1,sha2:sub2:url2"
    mappings = {}
    for entry in mapping_str.split(","):
        if ":" in entry:
            sha, sub, url = entry.split(":", 2)
            mappings[sha] = (sub, url)
            
    with open(filepath, "r") as f:
        lines = f.readlines()
        
    out_lines = []
    for line in lines:
        out_lines.append(line)
        if line.startswith("pick "):
            sha = line.split(" ")[1][:7]
            # If this SHA needs an update, inject an exec line right after the pick
            for mapped_sha, (sub, url) in mappings.items():
                if sha.startswith(mapped_sha) or mapped_sha.startswith(sha):
                    exec_cmd = f"exec git config --file .gitmodules submodule.{sub}.url {url} && git add .gitmodules && git commit --amend --no-edit\n"
                    out_lines.append(exec_cmd)
                    
    with open(filepath, "w") as f:
        f.writelines(out_lines)

def main():
    if len(sys.argv) == 2 and sys.argv[1].endswith("git-rebase-todo"):
        sequence_editor_mode(sys.argv[1])
        return

    reg_urls = get_gitmodules_urls()
    if not reg_urls:
         print("No submodules found in .gitmodules.")
         return

    discrepancies = []
    for sub, reg_url in reg_urls.items():
        if os.path.exists(os.path.join(sub, ".git")):
            res = subprocess.run(["git", "-C", sub, "remote", "get-url", "origin"], capture_output=True, text=True)
            if res.returncode == 0:
                actual_url = res.stdout.strip()
                if actual_url != reg_url:
                    discrepancies.append((sub, reg_url, actual_url))

    if not discrepancies:
        print("All submodule URLs in .gitmodules perfectly match their internal origin remotes.")
        return

    print(f"Found {len(discrepancies)} URL discrepancies. Constructing dynamic rebase sequence...\n")

    mappings = []
    for sub, original_url, actual_url in discrepancies:
        sha = get_origin_commit_for_submodule(sub)
        if sha:
            mappings.append(f"{sha}:{sub}:{actual_url}")
            
            # Secure upstream remote immediately
            chk = subprocess.run(["git", "-C", sub, "remote", "get-url", "upstream"], capture_output=True)
            if chk.returncode != 0:
                subprocess.run(["git", "-C", sub, "remote", "add", "upstream", original_url])
        else:
            print(f"  -> WARNING: Could not find origin commit for {sub}")

    if not mappings:
        print("No origin commits found. Aborting.")
        return
        
    mapping_str = ",".join(mappings)
    
    # Establish environment for rebase
    env = os.environ.copy()
    env["SYNC_MAPPINGS"] = mapping_str
    # We call ourselves dynamically as the sequence editor!
    script_path = os.path.abspath(__file__)
    env["GIT_SEQUENCE_EDITOR"] = f"python3 {script_path}"
    env["PAGER"] = "cat"
    
    # Trigger rebase
    print("Executing automated inline history rewriting (exec-squash)...")
    base_commit = subprocess.run(["git", "merge-base", "HEAD", "origin/main"], capture_output=True, text=True).stdout.strip()
    res = subprocess.run(["git", "rebase", "-i", base_commit], env=env)
    
    if res.returncode == 0:
        print("\n[!] Synchronization complete. Historical submodules successfully aligned.")
    else:
        print("\n[!] Rebase encountered an anomaly. Please resolve via git status.")

if __name__ == "__main__":
    main()
