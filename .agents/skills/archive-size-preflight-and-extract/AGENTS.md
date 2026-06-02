# AGENTS.md — archive-size-preflight-and-extract

This is the companion bridge file for the `archive-size-preflight-and-extract` skill.

For the active operational protocol — **always** consult the SSOT:

→ [`SKILL.md`](./SKILL.md)

## Quick context (passive)

- **Purpose**: Pre-flight an archive (`.zip`, `.7z`, `.tar.gz`, ...) with 7-Zip to
  report compressed-on-disk size, uncompressed total, file count, folder count, and
  compression ratio **before** paying the disk-space cost of extraction; then extract
  reliably to a sibling folder of the same name with progress feedback and verify the
  extracted footprint.
- **Tool**: 7-Zip CLI (`7z.exe`), discovered via PATH → `C:\Program Files\7-Zip\7z.exe`
  → `C:\Program Files (x86)\7-Zip\7z.exe`.
- **Artifacts shipped**:
    - [`scripts/Get-ArchiveSizeReport.ps1`](./scripts/Get-ArchiveSizeReport.ps1) — Phase 1 + 2 (sizes, counts, ratio)
    - [`scripts/Expand-ArchiveWithVerification.ps1`](./scripts/Expand-ArchiveWithVerification.ps1) — Phase 3 + 4 (extract + verify)
- **Cluster-overhead caveat**: When `FileCount > 10 000`, the agent MUST warn the
  user that NTFS 4 KiB cluster allocation rounds every small file up — on-disk
  footprint can meaningfully exceed `UncompressedBytes`.
- **Why not `Expand-Archive`**: slow on large archives; the .NET ZipFile API on
  Windows PowerShell 5.1 silently truncates entries > 4 GB; no progress feedback.
