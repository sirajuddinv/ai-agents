# AGENTS.md (Work Log Processing)

Refer to [SKILL.md](./SKILL.md) for the active operational protocol for transforming rough work log files into formatted work log files.

## When to Use

- User provides a `*_rough.txt` file and asks to process it like a reference file (e.g., `jan2026.txt`)
- User asks to transform work log entries into standardized format
- User asks to "process" or "format" a work log file

## Mandates

- **Reference Format MUST be read first** before transformation
- **Zero Omission**: All entries from rough file MUST be preserved in output
- **Day of Week**: All dates MUST have day of week added
- **Caller Format**: All calls/voice/team events MUST use `(Name)` notation

## Related Skills

- [Text to Markdown](./text_to_markdown/SKILL.md) - For plain text to markdown conversion
- [Redaction & Portability](./redaction_portability/SKILL.md) - For sensitive information handling