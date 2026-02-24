<!--
title: Eclipse PDE Runtime Troubleshooting
description: Diagnose and fix "Unresolved compilation problems" java.lang.Error crashes in Eclipse PDE/OSGi headless applications — caused by workspace projects with broken dependencies shadowing working target platform JARs.
category: Eclipse PDE Runtime
-->

# Eclipse PDE Runtime Troubleshooting Skill

> **Skill ID:** `eclipse_pde_runtime_troubleshooting`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Diagnose and resolve `java.lang.Error: Unresolved compilation problems`
crashes in Eclipse PDE/OSGi headless applications. These errors occur
when an Eclipse workspace project has broken dependencies, causing the
JDT compiler to produce `.class` files with error stubs. At runtime,
the OSGi framework loads the error-stubbed class instead of the working
version from the target platform JAR, and the JVM throws a fatal
`java.lang.Error`.

This is a common pattern in any Eclipse PDE workspace when projects
with complex dependency chains (Xtext grammars, code generators, EMF
models) are opened alongside the main development projects.

## Prerequisites

| Requirement | Minimum |
|---|---|
| Workspace | An Eclipse PDE workspace with OSGi bundles |
| Runtime | Eclipse PDE launch configuration (`.launch` file) |
| VCS | Git 2.x+ (for verifying no code changes caused the issue) |

## When to Apply

Apply this skill when:

- A runtime error contains `java.lang.Error: Unresolved compilation
  problems` with one or more `cannot be resolved to a type` messages
- The error occurs during execution of an Eclipse/OSGi headless
  application (e.g., BeanShell script invocation with `bsh.BSH*`
  stack frames)
- The error mentions `The import <package> cannot be resolved` for
  a package that clearly exists in the workspace or target platform
- The error references `*Impl` classes from EMF-generated code
- A user reports "it was working before and now it crashes" without
  code changes

Do NOT apply when:

- The error is a `ClassNotFoundException` (missing bundle, not broken
  compilation)
- The error is a `NoClassDefFoundError` (class loading order issue,
  not compilation)
- The error is a compile-time error in the Eclipse Problems view (fix
  the code, don't troubleshoot runtime)
- The user is actively developing the project that has the error (they
  need to fix their code, not close the project)

---

## Symptom Recognition

### Error Signature

The canonical error pattern looks like:

```
Target exception: java.lang.Error: Unresolved compilation problems:
    The import <package> cannot be resolved
    <ClassName> cannot be resolved to a type
    <ClassName> cannot be resolved to a type
    ...
    The method <methodName>() from the type <TypeImpl> refers to the missing type <ClassName>
```

### Key Indicators

| Indicator | What It Tells You |
|---|---|
| `java.lang.Error` (not Exception) | JDT compiled with errors — this is a compile stub, not a runtime bug |
| `cannot be resolved to a type` repeated many times | An entire package/bundle is invisible to the compiler |
| `The import ... cannot be resolved` | The dependent bundle is not on the compile classpath |
| `refers to the missing type` | A generated `*Impl` class has methods that return the unresolvable type |
| Application ran partway before crashing | The broken bundle was only loaded on demand, not at startup |

### Distinguishing from Other Errors

| Error Type | Cause | Fix |
|---|---|---|
| `Unresolved compilation problems` | JDT error stubs in `.class` files | **This skill** — close/fix the project |
| `ClassNotFoundException` | Bundle not in launch config | Add bundle to `.launch` file |
| `NoClassDefFoundError` | Class loaded before its dependency | Fix bundle start levels in `.launch` |
| `LinkageError` | Version conflict between bundles | Resolve duplicate bundle versions |

---

## Root Cause Analysis

### The Shadowing Mechanism

Eclipse PDE launch configurations resolve bundles from two sources:

1. **Workspace bundles** — Projects open in the Eclipse workspace
   (compiled by JDT in real-time)
2. **Target platform bundles** — Pre-built JARs in the target platform

**Workspace projects always take precedence over target platform JARs**
with the same `Bundle-SymbolicName`. This is by design — it allows
developers to modify and test plugins without rebuilding the entire
platform.

### The Failure Chain

```
1. Project A is open in workspace
     ↓
2. Project A has MANIFEST.MF dependencies on bundles not available
   in the workspace or target platform
     ↓
3. JDT cannot compile Project A → .class files contain error stubs
     ↓
4. Project B depends on Project A via Require-Bundle
     ↓
5. JDT compiles Project B but cannot resolve types from Project A
   → Project B's .class files also contain error stubs
     ↓
6. At runtime, OSGi loads Project B's error-stubbed .class from
   workspace instead of the working .class from the target platform JAR
     ↓
7. java.lang.Error: Unresolved compilation problems
```

### Why It Wasn't Always Broken

The workspace project was likely:

- Recently imported or re-opened (was previously closed)
- Had its target platform changed (missing bundles)
- Had dependencies updated that broke the build
- Was opened alongside other projects for the first time

---

## Step-by-Step Diagnostic Procedure

### Step 1 — Extract the Missing Type

From the error message, identify:

1. **The missing type** — the class that "cannot be resolved"
2. **The missing package** — the import that cannot be resolved
3. **The affected type** — the `*Impl` class with error stubs

### Step 2 — Locate the Source Project

Find which workspace project provides the missing type:

```powershell
Get-ChildItem -Path "<workspace_root>" -Recurse -Filter "<MissingType>.java" |
    Select-Object FullName
```

This identifies the **source project** that exports the missing package.

### Step 3 — Check the Source Project's Dependencies

Read the source project's `META-INF/MANIFEST.MF`:

```powershell
Get-Content "<source_project>/META-INF/MANIFEST.MF"
```

Look at the `Require-Bundle` list. Each dependency must be either:

- Another open workspace project, OR
- A JAR in the target platform

### Step 4 — Check for Build Errors

In Eclipse: **Problems view → filter to the source project**

In VS Code: Use `get_errors` tool filtered to the project path.

### Step 5 — Check the Launch Configuration

Read the `.launch` file used to run the application:

```powershell
Select-String -Path "<launch_file>" -Pattern "<source_bundle_name>"
```

Determine if the source project is listed in:

- `selected_workspace_bundles` — loaded from workspace (compiled by JDT)
- `selected_target_bundles` — loaded from target platform JAR

---

## Fix Options

### Option A — Close the Project (Recommended)

**When to use:** You do NOT need to modify the source project. You only
need its compiled classes at runtime.

**Procedure:**

1. In Eclipse: Right-click the source project → **Close Project**
2. The OSGi framework will now resolve the bundle from the target
   platform JAR instead of the workspace
3. **Clean & Rebuild** the workspace: Project → Clean → Clean all
   projects
4. Re-run the launch configuration

**Why this works:** Closing the project removes it from the workspace
bundle list. OSGi falls back to the target platform JAR, which was
compiled with all dependencies present.

**Verification:**

```powershell
# Re-run the application — should no longer crash
# The log should proceed past the previously failing phase
```

### Option B — Fix the Dependencies

**When to use:** You need to actively develop the source project.

**Procedure:**

1. Check the source project's `MANIFEST.MF` `Require-Bundle` list
2. For each missing dependency, either:
   - Import the dependency project into the workspace, OR
   - Add the dependency JAR to the target platform
3. Clean & Rebuild the workspace
4. Verify no errors in the Problems view for the source project

### Option C — Add to Launch Config

**When to use:** The project compiles fine but is missing from the
launch configuration's workspace bundles list.

**Procedure:**

1. Open the `.launch` file
2. Add the missing bundle to `selected_workspace_bundles`:

```xml
<setEntry value="<bundle.symbolic.name>@default:default"/>
```

3. Re-run the launch configuration

**Note:** This is rarely the fix for `Unresolved compilation problems`.
It's more relevant for `ClassNotFoundException`.

---

## Known Instances

### DGS-ICE: CallGraphService / com.bosch.dgs.ice.mcop.cgg

**First observed:** 2026-02-24

**Symptom:**

```
java.lang.Error: Unresolved compilation problems:
    The import com.bosch.dgs.ice.mcop.cgg cannot be resolved
    CallGraphService cannot be resolved to a type
    ...
    The method getCallGraphMap() from the type McopModelCoreImpl
    refers to the missing type CallGraphService
```

**Root cause:** `com.bosch.dgs.ice.mcop.cgg` was open in the workspace.
Its `MANIFEST.MF` requires `org.eclipse.xtext` and
`com.bosch.ara2l.core.loggingframework`, which were not fully available
in the target platform. JDT could not compile `CallGraphService.java` →
`com.bosch.dgs.ice.mcop.core` (which depends on `mcop.cgg`) also got
error stubs in `McopModelCoreImpl.class`.

**Fix applied:** Option A — closed `com.bosch.dgs.ice.mcop.cgg` project.
OSGi fell back to the working target platform JAR
(`com.bosch.dgs.ice.mcop.cgg_1.0.0.202011182002.jar`).

**Affected launch configs:** All launch configs in
`com.bosch.dgs.ice.dcg.product/` had `com.bosch.dgs.ice.mcop.cgg`
missing from `selected_workspace_bundles` but listed
`com.bosch.dgs.ice.mcop.core` (which depends on it). The dependency
was satisfied by the target platform JAR when the project was closed.

---

## Prevention

### Launch Config Workspace Bundles Audit

Before running, verify that every workspace bundle's dependencies are
satisfied. For each entry in `selected_workspace_bundles`, check:

1. Is the project open in the workspace?
2. Does it compile without errors?
3. Are all its `Require-Bundle` dependencies either:
   - Also in `selected_workspace_bundles`, OR
   - Available as JARs in `selected_target_bundles`?

### Projects to Keep Closed

Projects with complex external dependencies (Xtext, grammar
infrastructure, code generators) that are often unavailable in
development target platforms should be kept closed unless actively
modifying them. The target platform JAR provides the working
compiled classes.

### Quick Smoke Test

After opening/importing new projects, run a quick validation before
full execution:

1. Check Eclipse Problems view for `Unresolved compilation` errors
2. If any exist in projects you're not modifying → close them
3. Clean & Rebuild
4. Re-run

---

## Prohibited Behaviors

The agent is **BLOCKED** from:

- **Modifying the source project's code to remove the dependency** —
  The dependency exists for a reason. The fix is to provide the
  dependency or close the project, not remove it.
- **Deleting .class files manually** — JDT manages the `bin/` folder.
  Use Clean & Rebuild instead.
- **Modifying target platform configurations** — These are shared team
  artifacts. Adding JARs to the target platform requires team
  coordination.
- **Auto-closing projects without user approval** — Closing a project
  may have side effects. Always ask first.

---

## Common Pitfalls

| Pitfall | Solution |
|---|---|
| Confusing `java.lang.Error` with `Exception` | `Error` means JDT error stubs — this is a build issue, not a runtime bug |
| Trying to fix the `*Impl` class (e.g., generated EMF code) | The `*Impl` class is EMF-generated. Fix the SOURCE project that provides the missing type. |
| Rebuilding without closing the broken project | Rebuild alone doesn't help if the dependency is still missing. Close first, then rebuild. |
| Assuming the `.launch` file is wrong | The `.launch` file is usually correct. The issue is the workspace project shadowing the working JAR. |
| Searching for the error in recently modified files | This error is caused by workspace configuration, not code changes. Check which projects are open. |
| Opening a project "just to look at the code" | Opening it triggers JDT compilation. Use `read_file` in VS Code or browse in a file explorer instead. |

---

## Checklist

Before reporting the issue as resolved, verify:

- [ ] Root cause identified — which project has broken dependencies
- [ ] Fix applied — project closed (Option A) or dependencies fixed
  (Option B)
- [ ] Workspace cleaned and rebuilt
- [ ] Application re-run successfully — no `Unresolved compilation
  problems` error
- [ ] Application proceeds past the previously failing phase
- [ ] No unintended projects were closed
