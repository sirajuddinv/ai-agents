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

def run_audit(sha, cwd=None):
    """Run the audit.py script and return the output."""
    try:
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
        script_relative = ".agents/skills/git_commit_details_audit/scripts/audit.py"
        abs_script_path = os.path.join(root, script_relative)
        
        result = subprocess.run(
            ["python3", abs_script_path, sha],
            cwd=cwd or root,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def parse_audit_output(output):
    """Deeply parse the audit.py output to map submodules and reachability."""
    if not output: return None
    
    data = {
        "author": "Unknown", "date": "Unknown", "message": "N/A", "repo": "Unknown",
        "submodules": {}, # name -> pointer
        "reachability": [] # list of {type, name, tip, status}
    }
    
    # Simple Metadata
    m = re.search(r"Author: (.*)", output); d1 = m.group(1).strip() if m else "Unknown"
    m = re.search(r"Date: (.*)", output); d2 = m.group(1).strip() if m else "Unknown"
    m = re.search(r"Commit Message: (.*)", output); d3 = m.group(1).strip() if m else "N/A"
    m = re.search(r"Repository: (.*)", output); d4 = m.group(1).strip() if m else "Unknown"
    data.update({"author": d1, "date": d2, "message": d3, "repo": d4})
    
    # Submodule Differential Analysis
    diff_blocks = re.split(r"diff --git a/", output)
    for block in diff_blocks[1:]:
        name_match = re.search(r"^([^\s]+)", block)
        if name_match:
            sub_name = name_match.group(1).strip()
            ptr_match = re.search(r"\+Subproject commit ([0-9a-f]+)", block)
            if ptr_match:
                data["submodules"][sub_name] = ptr_match.group(1)
    
    # Reachability Parsing (REFERENCE AUDIT table)
    ref_section = re.search(r"### REFERENCE AUDIT.*?\n(.*?)\n\n|### REFERENCE AUDIT.*?\n(.*)$", output, re.S)
    if ref_section:
        table_text = ref_section.group(1) or ref_section.group(2)
        if table_text:
            lines = table_text.strip().splitlines()
            for line in lines:
                if "|" in line and ":---" not in line and "Type | Name" not in line:
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 4:
                        data["reachability"].append({
                            "type": parts[0],
                            "name": parts[1],
                            "tip": parts[2],
                            "status": parts[3]
                        })
                
    return data

def get_pointer_distance(p1, p2, cwd):
    """Determine alignment and depth between two pointers."""
    if not os.path.isdir(cwd): return "Missing Directory"
    c1 = run_git(["rev-list", "--count", f"{p1}..{p2}"], cwd=cwd)
    c2 = run_git(["rev-list", "--count", f"{p2}..{p1}"], cwd=cwd)
    try:
        d1, d2 = int(c1 or 0), int(c2 or 0)
        if d1 > 0: return f"Forward by {d1} commits"
        if d2 > 0: return f"Backward by {d2} commits"
        return "Identical Origin/Diverged"
    except: return "Unknown Alignment"

def compare_commits(sha1, sha2):
    """Synthesize the final v2.3 comparison report."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
    r1 = run_audit(sha1); r2 = run_audit(sha2)
    if not r1 or not r2: return "Error: Failed to orchestrate audits."
    
    d1 = parse_audit_output(r1); d2 = parse_audit_output(r2)
    output = []
    output.append(f"# Comparative Audit: {sha1} vs. {sha2}")
    
    # 1. High-Fidelity Pointer Comparison
    output.append("\n## 1. High-Fidelity Pointer Comparison")
    output.append("| Attribute | Commit {0} | Commit {1} |".format(sha1[:7], sha2[:7]))
    output.append("| :--- | :--- | :--- |")
    output.append(f"| **AUTHOR** | {d1['author']} | {d2['author']} |")
    output.append(f"| **DATE** | {d1['date']} | {d2['date']} |")
    output.append(f"| **MESSAGE** | {d1['message'][:65]}... | {d2['message'][:65]}... |")
    
    common_subs = set(d1["submodules"].keys()) & set(d2["submodules"].keys())
    for sub in common_subs:
        p1, p2 = d1["submodules"][sub], d2["submodules"][sub]
        status = get_pointer_distance(p1, p2, os.path.join(root, sub))
        output.append(f"| **SUBMODULE ({sub})** | `{p1[:8]}` | `{p2[:8]}` |")
        output.append(f"| *Alignment Info* | --- | *{status}* |")

    # Reachability Audit (New for v2.3)
    output.append("\n### Reachability Audit (Branches & Tags)")
    all_refs = set([(r["type"], r["name"]) for r in d1["reachability"]]) | \
               set([(r["type"], r["name"]) for r in d2["reachability"]])
    
    if all_refs:
        output.append("| Type | Name | Status ({0}) | Status ({1}) |".format(sha1[:7], sha2[:7]))
        output.append("| :--- | :--- | :--- | :--- |")
        for rtype, rname in sorted(all_refs):
            s1 = next((r["status"] for r in d1["reachability"] if r["type"] == rtype and r["name"] == rname), "N/A")
            s2 = next((r["status"] for r in d2["reachability"] if r["type"] == rtype and r["name"] == rname), "N/A")
            output.append(f"| {rtype} | {rname} | {s1} | {s2} |")
    else:
        output.append("No common branch/tag references found.")

    # 2. Recursive History Audit Results
    output.append("\n## 2. Recursive History Audit Results")
    for sub in common_subs:
        p1, p2 = d1["submodules"][sub], d2["submodules"][sub]
        if p1 != p2:
            output.append(f"\n### Deep Audit: Submodule `{sub}`")
            rs1 = run_audit(p1, cwd=os.path.join(root, sub))
            rs2 = run_audit(p2, cwd=os.path.join(root, sub))
            if rs1 and rs2:
                sd1, sd2 = parse_audit_output(rs1), parse_audit_output(rs2)
                output.append("| Internal Delta | Sub-Commit {0} | Sub-Commit {1} |".format(p1[:7], p2[:7]))
                output.append("| :--- | :--- | :--- |")
                output.append(f"| Message | {sd1['message']} | {sd2['message']} |")
                output.append(f"| Author | {sd1['author']} | {sd2['author']} |")
            else:
                output.append("> [!WARNING] Recursive audit failed.")

    # 3. High-Level Impact: "Why vs. What"
    output.append("\n## 3. High-Level Impact: 'Why vs. What'")
    summary = []
    if d1["message"] == d2["message"]: summary.append("Duplicate commit messages detected (Rebase variant).")
    for sub in common_subs:
        if d1["submodules"][sub] != d2["submodules"][sub]:
            summary.append(f"Submodule `{sub}` pointer mismatch ({get_pointer_distance(d1['submodules'][sub], d2['submodules'][sub], os.path.join(root, sub))}).")
    
    dtext = " ".join(summary) if summary else "No significant technical delta."
    output.append(f"\n**The What**: {dtext}")
    output.append("\n**The Why**: [Describe the historical rationale here, e.g. 'Backup variant vs. Main alignment']")
    
    return "\n".join(output)

if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(1)
    print(compare_commits(sys.argv[1], sys.argv[2]))
