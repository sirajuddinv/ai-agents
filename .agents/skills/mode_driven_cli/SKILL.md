<!--
title: Mode-Driven CLI
description: Replace variable-argument CLI parsing with a fixed-position, mode-driven interface backed by an enum — eliminating argument ambiguity and enabling self-documenting usage strings.
category: CLI & Application Architecture
-->

# Mode-Driven CLI Skill

> **Skill ID:** `mode_driven_cli`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Refactor a command-line application that accepts a variable number of
arguments (where argument count depends on the selected mode) into a
unified, fixed-position argument format backed by a mode enum.

Variable-argument CLIs create ambiguity — users must memorize which
modes need which files, error messages are vague, and the parsing code
branches on argument count. A mode-driven CLI solves this by:

1. Defining a **mode enum** that declares each mode's metadata (which
   inputs it needs, display name, usage string).
2. Enforcing a **fixed argument count** with a sentinel value (e.g.,
   `NA`) for inputs that a particular mode does not use.
3. Letting the enum generate **self-documenting usage strings** that
   show the user exactly which arguments to supply and which to mark
   as `NA`.

The result is a CLI that is consistent, self-documenting, and trivial
to extend with new modes.

## Prerequisites

| Requirement | Minimum |
|---|---|
| Language | Java 8+ (enum support; adaptable to C#, Python, Kotlin) |
| Shell | PowerShell 5.1+ or Bash 4+ (for testing) |
| VCS | Git (for atomic commits of the refactoring) |

## When to Apply

Apply this skill when:

- A CLI application has different argument counts per mode
  (e.g., 3 args for mode A, 4 args for mode B)
- Usage strings are scattered across `if-else` branches or switch cases
- Adding a new mode requires touching the argument parser, usage printer,
  and dispatch logic separately
- Users report confusion about which arguments to pass for which mode
- The application has a "run all modes" meta-mode that orchestrates
  individual modes

Do NOT apply when:

- The CLI uses a mature argument-parsing library (e.g., Apache Commons
  CLI, picocli, argparse) that already handles subcommands
- The application has only one mode and no plans for additional modes
- The argument positions are genuinely different per mode (not just
  optional — truly different semantics)

---

## Step-by-Step Procedure

### Step 1 — Inventory Current Modes and Arguments

List every mode the application supports and document the current
argument format for each.

Create a table like this:

| Mode | Current Args | Needs File A | Needs File B |
|---|---|---|---|
| FM | `<fileA> <outDir> FM` | Yes | No |
| PIB | `<fileB> <outDir> PIB` | No | Yes |
| ALL | `<fileA> <fileB> <outDir> ALL` | Yes | Yes |

Identify the **superset** — the maximum number of distinct arguments
across all modes. This becomes the fixed argument count.

### Step 2 — Define the Mode Enum

Create an enum that encodes each mode's metadata:

```java
public enum ConversionMode {
    FM("Firmware",   true,  false),
    PIB("PIB",       false, true),
    ALL("All Modes", true,  true);

    private final String displayName;
    private final boolean needsFileA;
    private final boolean needsFileB;

    ConversionMode(String displayName, boolean needsFileA,
                   boolean needsFileB) {
        this.displayName = displayName;
        this.needsFileA = needsFileA;
        this.needsFileB = needsFileB;
    }

    public String displayName() { return displayName; }
    public boolean needsFileA() { return needsFileA; }
    public boolean needsFileB() { return needsFileB; }
}
```

#### Enum Design Rules

- **Self-documenting**: Every mode carries its own display name, input
  requirements, and (optionally) logging/telemetry identifiers.
- **Parsing**: Add a `fromString(String)` static method that matches
  case-insensitively and throws a clear error for unknown modes.
- **Usage generation**: Add a `usageString()` method that builds the
  usage hint dynamically based on which inputs the mode needs:

```java
public String usageString() {
    String fileA = needsFileA ? "<FILE_A>" : "NA";
    String fileB = needsFileB ? "<FILE_B>" : "NA";
    return String.format("  %s %s <OUTPUT_DIR> %s",
                         fileA, fileB, name());
}
```

- **Extensibility**: Adding a new mode is a single enum constant —
  no changes to the argument parser or usage printer.

### Step 3 — Choose a Sentinel Value

Define a constant for the "not applicable" sentinel:

```java
public static final String NA_ARG = "NA";
```

Rules for the sentinel:

- Must be a value that cannot collide with valid file paths
- Must be case-insensitive in comparison (`"NA"`, `"na"`, `"Na"` all match)
- Must be documented in the usage output
- Must be checked **before** any file validation (do not attempt to
  open a file called "NA")

### Step 4 — Rewrite the Argument Parser

Replace variable-length argument parsing with fixed-position parsing:

```java
// BEFORE — variable arg count
if (args.length == 3) {
    // mode determines which file arg[0] is
} else if (args.length == 4) {
    // different layout
}

// AFTER — fixed 4-arg format
if (args.length != EXPECTED_ARG_COUNT) {
    printUsage();
    System.exit(1);
}
String fileA   = args[0];  // or NA
String fileB   = args[1];  // or NA
String outDir  = args[2];
String modeStr = args[3];

ConversionMode mode = ConversionMode.fromString(modeStr);
```

#### Argument Validation Rules

After parsing, validate that the mode's required inputs are not `NA`
and that unrequired inputs **are** `NA`:

```java
if (mode.needsFileA() && NA_ARG.equalsIgnoreCase(fileA)) {
    logger.error(mode.displayName() + " requires <FILE_A>");
    System.exit(1);
}
if (!mode.needsFileA() && !NA_ARG.equalsIgnoreCase(fileA)) {
    logger.warn(mode.displayName()
        + " does not use <FILE_A>; ignoring provided value");
}
```

### Step 5 — Refactor the Dispatch Logic

Replace switch/if-else dispatch with enum-driven dispatch:

```java
private void runConverter(ConversionMode mode, String fileA,
                          String fileB, String outDir) {
    switch (mode) {
        case FM:  new FirmwareConverter().convert(fileA, outDir); break;
        case PIB: new PibConverter().convert(fileB, outDir);      break;
        case ALL:
            runConverter(ConversionMode.FM, fileA, fileB, outDir);
            runConverter(ConversionMode.PIB, fileA, fileB, outDir);
            break;
    }
}
```

For a meta-mode (e.g., `ALL`) that runs multiple modes in sequence,
iterate over the enum values and filter by the meta-mode's needs.

### Step 6 — Update Usage Output

Generate usage output dynamically from the enum:

```java
private static void printUsage() {
    System.out.println("Usage:");
    for (ConversionMode m : ConversionMode.values()) {
        System.out.println(m.usageString());
    }
    System.out.println();
    System.out.println("Use NA for arguments not required by the mode.");
}
```

This ensures usage strings are always in sync with the enum — adding
a new mode automatically updates the help text.

### Step 7 — Eliminate System.exit() from Converters

As part of this refactoring, remove `System.exit(0)` calls from
individual converter classes. Converters should return normally on
success and throw exceptions on failure. Only the main entry point
should call `System.exit()`.

```java
// BEFORE (inside converter)
System.exit(0);

// AFTER (inside converter)
return;
```

This makes converters composable — the ALL meta-mode can call them
sequentially without the first converter terminating the JVM.

### Step 8 — Verify All Modes

Test every mode, including the meta-mode and error cases:

```powershell
# Mode that needs only fileA
java -cp "libs/*;bin" com.example.App sample.dat NA output FM

# Mode that needs only fileB
java -cp "libs/*;bin" com.example.App NA sample.pib output PIB

# Meta-mode that needs both
java -cp "libs/*;bin" com.example.App sample.dat sample.pib output ALL

# Error: missing required input
java -cp "libs/*;bin" com.example.App NA NA output FM
# Expected: error message about FM requiring fileA

# Error: unknown mode
java -cp "libs/*;bin" com.example.App NA NA output INVALID
# Expected: error message listing valid modes
```

---

## Verification Checklist

| # | Check | Pass |
|---|---|---|
| 1 | Enum has one constant per mode with correct `needs*` flags | ☐ |
| 2 | `fromString()` is case-insensitive and rejects unknown modes | ☐ |
| 3 | `usageString()` shows `NA` for unrequired arguments | ☐ |
| 4 | Argument parser enforces exactly N arguments | ☐ |
| 5 | NA sentinel is checked before file validation | ☐ |
| 6 | All converters return normally (no `System.exit(0)`) | ☐ |
| 7 | Meta-mode (ALL) successfully chains sub-modes | ☐ |
| 8 | Usage output is generated from the enum, not hardcoded | ☐ |
| 9 | Error messages name the mode and the missing argument | ☐ |
| 10 | Clean compilation with no warnings | ☐ |

---

## Anti-Patterns

| Pattern | Why It Fails |
|---|---|
| Parsing by `args.length` with different layouts per count | Adding a mode requires changing every branch; easy to mis-index |
| Hardcoded usage strings per mode | Usage drifts out of sync with actual parsing logic |
| `System.exit(0)` inside converters | Prevents composition in meta-modes; kills JVM mid-sequence |
| Optional arguments without sentinels | Ambiguous — is `args[1]` the output dir or the second file? |
| Case-sensitive mode matching | Users type `all`, `All`, or `ALL` — all must work |

---

## Reference Implementation

The PLC Converter project applied this skill to unify a 3-or-4 argument
CLI into a fixed 4-argument format:

```
<NVM_FILE|NA> <PIB_FILE|NA> <OUTPUT_DIR> <MODE>
```

- **Enum**: `ConversionMode` — 6 modes (FM, MC, PIB, DCM, HEX, ALL)
  with `needsNvm`, `needsPib`, `displayName()`, `usageString()`
- **Sentinel**: `PLCConstants.NA_ARG = "NA"`
- **Meta-mode**: ALL runs FM → MC → PIB → DCM → HEX in sequence
- **Key files**: `ConversionMode.java`, `PLCConstants.java`,
  `Application.java`
