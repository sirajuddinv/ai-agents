#!/usr/bin/env python3
"""Extract and compare OSGi MANIFEST.MF headers between two bundles.

The deterministic core of Maven/Tycho build-failure analysis: given two
OSGi bundle JARs (or two already-extracted MANIFEST.MF files), this script
unfolds the continuation-line-wrapped headers, extracts the dependency-bearing
OSGi headers, decodes the ``Bundle-Version`` qualifier timestamp, and reports
which ``Require-Bundle`` / ``Import-Package`` entries were ADDED or REMOVED
between the known-good and the broken bundle -- the single most common root
cause of a "Missing requirement ... could not be found" Tycho failure.

Language tier: Tier 1 (Python 3.12+) per scripting-language-selection-rules
section 3 -- the body is text/ZIP parsing and structured comparison, the
default tier for new scripts.

No third-party dependencies: ``zipfile`` reads the JAR, the rest is stdlib.

Usage
-----
    # Compare two bundle JARs
    python analyze_maven_build_failure.py --good old.jar --bad new.jar

    # Compare two extracted manifests
    python analyze_maven_build_failure.py --good a/MANIFEST.MF --bad b/MANIFEST.MF --manifest

    # Inspect a single bundle (headers + decoded qualifier)
    python analyze_maven_build_failure.py --good one.jar
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

# OSGi headers whose values are comma-separated dependency lists.
_LIST_HEADERS = ("Require-Bundle", "Import-Package", "Export-Package")
# OSGi headers reported verbatim (identity / environment).
_SCALAR_HEADERS = (
    "Bundle-SymbolicName",
    "Bundle-Version",
    "Bundle-Vendor",
    "Bundle-RequiredExecutionEnvironment",
)

_QUALIFIER_RE = re.compile(r"\.(\d{12})\b")


def read_manifest_text(path: Path, *, is_manifest: bool) -> str:
    """Return the raw MANIFEST.MF text from a JAR or a manifest file."""
    if is_manifest:
        return path.read_text(encoding="utf-8", errors="replace")
    with zipfile.ZipFile(path) as zf:
        with zf.open("META-INF/MANIFEST.MF") as fh:
            return fh.read().decode("utf-8", errors="replace")


def unfold(manifest_text: str) -> dict[str, str]:
    """Unfold OSGi continuation lines (leading single space) into headers.

    The OSGi/JAR manifest format wraps long values onto continuation lines
    that begin with exactly one space. Joining them restores the logical
    header value before parsing.
    """
    logical: list[str] = []
    for raw in manifest_text.splitlines():
        if raw.startswith(" ") and logical:
            logical[-1] += raw[1:]
        else:
            logical.append(raw)
    headers: dict[str, str] = {}
    for line in logical:
        if ":" in line:
            key, _, val = line.partition(":")
            headers[key.strip()] = val.strip()
    return headers


def split_list_header(value: str) -> list[str]:
    """Split a comma-separated OSGi header into bundle/package names.

    Commas inside attribute brackets (e.g. version ranges ``[1.0,2.0)``)
    are NOT treated as separators.
    """
    items: list[str] = []
    depth = 0
    current = ""
    for ch in value:
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            items.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        items.append(current.strip())
    # Strip per-entry attributes (everything after the first ';') for the name.
    return [item.split(";")[0].strip() for item in items if item.strip()]


def decode_qualifier(bundle_version: str) -> str | None:
    """Decode a 12-digit OSGi qualifier (yyyyMMddHHmm) to an ISO timestamp."""
    match = _QUALIFIER_RE.search(bundle_version)
    if not match:
        return None
    q = match.group(1)
    try:
        dt = datetime(
            int(q[0:4]), int(q[4:6]), int(q[6:8]),
            int(q[8:10]), int(q[10:12]), tzinfo=timezone.utc,
        )
    except ValueError:
        return None
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def report_single(label: str, headers: dict[str, str]) -> None:
    print(f"=== {label} ===")
    for key in _SCALAR_HEADERS:
        if key in headers:
            print(f"  {key}: {headers[key]}")
            if key == "Bundle-Version":
                ts = decode_qualifier(headers[key])
                if ts:
                    print(f"    -> qualifier build time: {ts}")
    for key in _LIST_HEADERS:
        if key in headers:
            entries = split_list_header(headers[key])
            print(f"  {key} ({len(entries)}):")
            for e in entries:
                print(f"    - {e}")
    print()


def compare(good: dict[str, str], bad: dict[str, str]) -> int:
    """Print added/removed dependency entries. Return process exit code."""
    report_single("KNOWN-GOOD", good)
    report_single("BROKEN", bad)

    changed = False
    print("=== DEPENDENCY DELTA (broken vs known-good) ===")
    for key in _LIST_HEADERS:
        good_set = set(split_list_header(good.get(key, "")))
        bad_set = set(split_list_header(bad.get(key, "")))
        added = sorted(bad_set - good_set)
        removed = sorted(good_set - bad_set)
        if added or removed:
            changed = True
            print(f"  {key}:")
            for a in added:
                print(f"    + ADDED:   {a}")
            for r in removed:
                print(f"    - REMOVED: {r}")
    if not changed:
        print("  (no Require-Bundle / Import-Package / Export-Package changes)")
    print()
    print(
        "NOTE: a newly ADDED Require-Bundle entry that is absent from every "
        "repository / component is the classic 'Missing requirement' root cause."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--good", required=True, type=Path,
                        help="Known-good bundle JAR (or MANIFEST.MF with --manifest)")
    parser.add_argument("--bad", type=Path,
                        help="Broken bundle JAR (or MANIFEST.MF with --manifest)")
    parser.add_argument("--manifest", action="store_true",
                        help="Inputs are extracted MANIFEST.MF files, not JARs")
    args = parser.parse_args(argv)

    try:
        good = unfold(read_manifest_text(args.good, is_manifest=args.manifest))
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        print(f"error reading --good: {exc}", file=sys.stderr)
        return 2

    if args.bad is None:
        report_single("BUNDLE", good)
        return 0

    try:
        bad = unfold(read_manifest_text(args.bad, is_manifest=args.manifest))
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        print(f"error reading --bad: {exc}", file=sys.stderr)
        return 2

    return compare(good, bad)


if __name__ == "__main__":
    raise SystemExit(main())
