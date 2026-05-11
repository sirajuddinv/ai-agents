# AGENTS.md — Eclipse Launch Stdout Capture

Companion bridge for this skill. The active SSOT is [`SKILL.md`](./SKILL.md).

## Purpose

Patch an Eclipse PDE `.launch` file so that the launched JVM's `System.out` and `System.err` are
captured to a file adjacent to the `.launch` file. Surfaces telemetry / lifecycle lines that bypass
the application's own log appenders (e.g., a `[telemetry ...]` exporter writing to a saved reference of the
original `PrintStream`, deliberately bypassing an `<host-logger>`-style `System.setOut(...)` swap).

## When the Agent Should Open This Skill

- The user asks "why don't I see the telemetry / TUL / lifecycle lines in `tool.log` / `<host>.log`?"
- The user asks to enable stdout capture for an Eclipse PDE launch.
- The user asks to patch a `.launch` file's *Common* tab Output File field from the command line.
- A telemetry resilience pattern is already integrated (see
  [`eclipse-pde-telemetry-resilience`](../eclipse-pde-telemetry-resilience/SKILL.md)) but the user has
  no captured artifact to verify the lifecycle catalogue against.

## Key Constraints

- The capture-file attribute lives in **`org.eclipse.debug.ui.*`**, **NOT** `org.eclipse.debug.core.*`.
  Wrong-package keys are silently ignored by Eclipse's UI loader.
- Eclipse caches `.launch` files in memory at IDE startup; disk edits require an F5 refresh or full
  restart to surface in the *Common* tab.
- **Never** click *Apply* in the Run Configurations dialog after an external disk edit until the dialog
  has been re-opened — *Apply* flushes the stale in-memory copy back to disk and erases the edit.
- *Delete* in Eclipse on a project-shared `.launch` file **physically removes the file**. Recover via
  `git checkout` or by re-patching.
- Eclipse snapshots launch attributes at JVM start. Edits during a run apply only to the **next** launch.

## Quick-Reference Patch

Insert exactly one line into the `<launchConfiguration>` root, after the
`org.eclipse.debug.core.preferred_launchers` map:

```xml
<stringAttribute key="org.eclipse.debug.ui.ATTR_CAPTURE_IN_FILE"
                 value="${workspace_loc:/<project-name>}/<launch-basename>.log"/>
```

Eclipse infers `capture_output=true` and `ATTR_APPEND_TO_FILE=false` defaults.

## Related Skills

- [`eclipse-pde-telemetry-resilience`](../eclipse-pde-telemetry-resilience/SKILL.md) — Emits the lines
  this skill captures.
- [`eclipse-pde-jdk-migration`](../eclipse-pde-jdk-migration/SKILL.md) — Sibling skill modifying the
  same `.launch` files for JRE-container migration.
