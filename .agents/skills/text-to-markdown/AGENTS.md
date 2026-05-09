---
name: Text to Markdown
description: Passive context bridge for converting structured plain-text data into formatted Markdown.
category: Data Formatting & Presentation
---

# Text to Markdown (Ref)

This bridge provides passive context for the `text-to-markdown` skill, which converts structured plain-text data
(delimiter-separated status trackers, lists, tables) into well-formatted Markdown with emoji status indicators,
proper tables, and file renaming.

It should be invoked whenever the user asks to convert plain-text data to Markdown, or whenever `.txt` files with
delimiter-separated status data are detected.

- **Primary Entry Point**: [.agents/skills/text-to-markdown/SKILL.md](./SKILL.md)
