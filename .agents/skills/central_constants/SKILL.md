<!--
title: Central Constants
description: Extract scattered raw strings, magic values, and duplicated literals into a single, authoritative constants class — eliminating typo risk and ensuring grep-ability.
category: Code Quality & Maintainability
-->

# Central Constants Skill

> **Skill ID:** `central_constants`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Audit a codebase for raw string literals, magic numbers, and duplicated
values scattered across multiple classes, then consolidate them into a
single authoritative constants class (or module). This skill covers:

1. **Detection** — find every raw literal that should be a constant.
2. **Classification** — group literals by domain (file extensions,
   tool names, status values, CLI labels, directory paths).
3. **Extraction** — create named constants with clear javadoc/comments.
4. **Replacement** — substitute every occurrence with the constant
   reference.
5. **Verification** — confirm zero remaining raw duplicates.

Centralising constants eliminates typo-induced bugs, makes values
grep-able from a single location, and turns "change one value" into
a one-line edit instead of a multi-file hunt.

## Prerequisites

| Requirement | Minimum |
|---|---|
| Language | Java 8+ (adaptable to C#, Python, TypeScript, Kotlin) |
| Shell | PowerShell 5.1+ or Bash 4+ |
| VCS | Git (for tracing blast radius of changes) |
| IDE | Any (Eclipse, IntelliJ, VS Code) — for rename refactoring |

## When to Apply

Apply this skill when:

- The same string literal appears in two or more source files
- File extensions are hardcoded as `".hex"`, `".nvm"`, `".pib"` etc.
- Tool names or executable paths are embedded in business logic
- Status values (`"SUCCESS"`, `"FAILURE"`) are used as raw strings
- Directory names (`"tools/"`) are hardcoded in multiple locations
- A rename or path change would require a multi-file search-and-replace
- Logging messages use inline strings that should reference constants

Do NOT apply when:

- The literal is truly local and used exactly once with no reuse risk
- The value is a log message template unique to one method
- Framework conventions require inline strings (e.g., annotation values
  in Spring `@Value("${property}")`)
- The project already uses a constants class and coverage is complete

---

## Step-by-Step Procedure

### Step 1 — Audit for Raw Literals

Search the entire source tree for string literals that appear more
than once or represent domain values.

#### 1a — Find Duplicate String Literals

```powershell
# Find all quoted strings in Java source files
Get-ChildItem -Recurse -Filter "*.java" |
    Select-String -Pattern '"[^"]{2,}"' -AllMatches |
    ForEach-Object { $_.Matches.Value } |
    Group-Object | Where-Object { $_.Count -gt 1 } |
    Sort-Object Count -Descending |
    Format-Table Count, Name -AutoSize
```

```bash
grep -roh '"[^"]\{2,\}"' src/ |
    sort | uniq -c | sort -rn |
    awk '$1 > 1'
```

#### 1b — Find Domain-Specific Patterns

Search for known patterns that should always be constants:

```powershell
# File extensions
Select-String -Path src/**/*.java -Pattern '"\.\w{2,4}"' -Recurse

# Executable names
Select-String -Path src/**/*.java -Pattern '"[\w]+\.exe"' -Recurse

# Directory paths
Select-String -Path src/**/*.java -Pattern '"tools[/\\]"' -Recurse

# Status strings
Select-String -Path src/**/*.java -Pattern '"(SUCCESS|FAILURE|PARTIAL)"' -Recurse
```

### Step 2 — Classify Constants by Domain

Group the discovered literals into logical categories. Use section
headers in the constants class to organise them:

| Category | Example Constants | Naming Pattern |
|---|---|---|
| File Extensions | `NVM_EXT`, `PIB_EXT`, `HEX_EXT` | `{FORMAT}_EXT` |
| Dot-prefixed Extensions | `DOT_NVM_EXT`, `DOT_PIB_EXT` | `DOT_{FORMAT}_EXT` |
| Tool Paths | `TOOLS_DIR`, `NVMSPLIT_EXE` | `{TOOL}_EXE` |
| Status Values | `STATUS_SUCCESS`, `STATUS_FAILURE` | `STATUS_{VALUE}` |
| CLI Labels | `ARG_INPUT_FILE`, `ARG_OUTPUT_DIR` | `ARG_{NAME}` |
| Application Identity | `APP_NAME`, `NA_ARG` | Descriptive |

### Step 3 — Create the Constants Class

Create a single class with `public static final` constants, organised
by domain with section-separator comments:

```java
public final class AppConstants {

    private AppConstants() { } // Prevent instantiation

    // ── File Extensions (without dot) ──────────────────────
    public static final String NVM_EXT = "nvm";
    public static final String PIB_EXT = "pib";
    public static final String HEX_EXT = "hex";

    // ── File Extensions (with dot) ─────────────────────────
    public static final String DOT_NVM_EXT = ".nvm";
    public static final String DOT_PIB_EXT = ".pib";
    public static final String DOT_HEX_EXT = ".hex";

    // ── Tool Paths ─────────────────────────────────────────
    public static final String TOOLS_DIR    = "tools";
    public static final String NVMSPLIT_EXE = "nvmsplit.exe";

    // ── Status Values ──────────────────────────────────────
    public static final String STATUS_SUCCESS = "SUCCESS";
    public static final String STATUS_FAILURE = "FAILURE";

    // ── Application Identity ───────────────────────────────
    public static final String APP_NAME = "PLC Converter";
    public static final String NA_ARG   = "NA";
}
```

#### Constants Class Design Rules

- **Private constructor** — constants classes must not be instantiable.
- **Section comments** — use visual separator lines (`// ── ... ──`)
  to group related constants.
- **Javadoc** — every constant gets a one-line javadoc comment
  explaining its purpose.
- **Dual-form extensions** — provide both with-dot and without-dot
  forms when both are used in the codebase (file filtering vs string
  replacement use different forms).
- **No logic** — the constants class contains only `static final`
  declarations. No methods, no computed values.

### Step 4 — Replace All Raw Literals

For each constant, find and replace every occurrence of the raw literal
with the constant reference.

**Process per constant:**

1. Search for the raw literal across all source files.
2. Replace with the constant reference (e.g., `".hex"` →
   `AppConstants.DOT_HEX_EXT`).
3. Add the import statement if not already present.
4. Compile to verify.

```powershell
# Find all usages of a raw literal
Select-String -Path src/**/*.java -Pattern '\.hex' -Recurse |
    Format-Table Filename, LineNumber, Line -AutoSize
```

#### Replacement Judgment Calls

Not every raw string should become a constant. Apply judgment:

| Keep as Raw String | Extract to Constant |
|---|---|
| Log message unique to one method | Status value used in multiple files |
| Javadoc text | File extension used in 2+ places |
| Test assertion message | Executable name referenced in code + build |
| Exception message unique to context | Directory name used in code + docs |

### Step 5 — Verify Zero Remaining Duplicates

After replacement, re-run the duplicate scan from Step 1a. The only
remaining duplicates should be:

- References to the constants class itself
- Genuinely unique log messages
- Framework-mandated inline strings

```powershell
# Verify: search for the old raw literal — should find only
# the constant definition itself
Select-String -Path src/**/*.java -Pattern '".hex"' -Recurse
# Expected: only AppConstants.java
```

### Step 6 — Compile and Test

```powershell
javac -cp "libs/*" -d bin src/**/*.java
```

Run the application through all modes to confirm behaviour is unchanged.
Constants extraction is a pure refactoring — no functional change.

---

## Verification Checklist

| # | Check | Pass |
|---|---|---|
| 1 | Constants class has private constructor | ☐ |
| 2 | Constants are grouped by domain with section headers | ☐ |
| 3 | Every constant has a javadoc comment | ☐ |
| 4 | No raw file extension strings remain in non-constants files | ☐ |
| 5 | No raw status strings remain in non-constants files | ☐ |
| 6 | No raw tool/executable names remain in business logic | ☐ |
| 7 | Imports added wherever constants are referenced | ☐ |
| 8 | Clean compilation with no warnings | ☐ |
| 9 | All modes produce identical output as before extraction | ☐ |

---

## Anti-Patterns

| Pattern | Why It Fails |
|---|---|
| Multiple constants classes per package | Splits the single source of truth; developers don't know where to look |
| Constants with computed values or method calls | Makes the class unpredictable; constants should be compile-time fixed |
| Over-extraction of unique log messages | Adds noise to the constants class without reducing duplication |
| Missing dual-form extensions | Forces callers to concatenate `"." + EXT` — error-prone and ugly |
| No section separators | 50+ constants in a flat list becomes unnavigable |
| `public` constants class without private constructor | Allows meaningless instantiation; signals design sloppiness |

---

## Reference Implementation

The PLC Converter project applied this skill to consolidate ~40 raw
literals into `PLCConstants.java`:

- **File extensions**: `NVM_EXT`, `PIB_EXT`, `HEX_EXT`, `DCM_EXT`
  (both with and without dot)
- **Tool paths**: `TOOLS_DIR`, `NVMSPLIT_EXE`, `SREC_CAT_EXE`
- **NVM suffixes**: `FM_NVM_SUFFIX` (`-00`), `MC_NVM_SUFFIX` (`-01`)
- **Status values**: `STATUS_SUCCESS`, `STATUS_FAILURE`, `STATUS_PARTIAL`
- **CLI labels**: `ARG_NVM_FILE`, `ARG_PIB_FILE`, `ARG_OUTPUT_DIR`
- **Application identity**: `APP_NAME`, `NA_ARG`
- **Key files**: `PLCConstants.java` (constants), 10+ consumer classes
