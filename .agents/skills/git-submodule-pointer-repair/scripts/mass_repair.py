#!/usr/bin/env python3
import sys
import os

# You MUST pass the path to git_filter_repo site-packages as the first argument,
# e.g., /Users/dk/.local/share/mise/installs/python/3.11.9/lib/python3.11/site-packages
if len(sys.argv) < 2:
    print("Usage: python3 mass_repair.py <path_to_site_packages>")
    sys.exit(1)

site_packages_path = sys.argv[1]
sys.path.insert(0, site_packages_path)
sys.argv.pop(1) # Remove the site-packages argument so filter-repo doesn't parse it

import git_filter_repo

# Load verified mapping (old_sha -> new_sha, both as bytes)
mapping = {}
with open("submodule_pointer_mapping_refined.txt") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            mapping[parts[0].encode()] = parts[1].encode()

replaced_count = [0]

def commit_callback(commit, metadata):
    for fc in commit.file_changes:
        if fc.mode == b'160000' and fc.blob_id in mapping:
            fc.blob_id = mapping[fc.blob_id]
            replaced_count[0] += 1

# --partial prevents touching backup/* branches; --refs limits scope to main
args = git_filter_repo.FilteringOptions.parse_args(
    ['--force', '--refs', 'main', '--partial'],
    error_on_empty=False
)
git_filter_repo.RepoFilter(args, commit_callback=commit_callback).run()
print(f"Replacements: {replaced_count[0]}")
