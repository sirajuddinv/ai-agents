---
name: JSON Deep Sort
description: Passive context bridge for alphabetical sorting of JSON arrays and recursive key ordering.
category: Data Processing
---

# JSON Deep Sort (Ref)

This bridge provides passive context for the `json-deep-sort` skill, which alphabetically sorts primitive JSON
arrays and recursively applies `sort_keys=True` for unified dictionary ordering — using native Python with no
third-party dependencies.

It should be invoked whenever the user asks to sort, normalize, or canonicalize a JSON file's keys or arrays for
diff stability or readability.

- **Primary Entry Point**: [.agents/skills/json-deep-sort/SKILL.md](./SKILL.md)
