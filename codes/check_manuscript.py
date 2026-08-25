#!/usr/bin/env python3
"""Fail-fast house-style and LaTeX-log checks for the revised manuscript."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FORBIDDEN_SOURCE = {
    r"(?<!\\)\\\(": r"use $...$ rather than \\(...\\)",
    r"(?<!\\)\\\[": r"use $$...$$ rather than \\[...\\]",
    r"\\leq(?!slant)": r"use \\leqslant",
    r"\\geq(?!slant)": r"use \\geqslant",
    r"\\le(?![A-Za-z])": r"use \\leqslant",
    r"\\ge(?![A-Za-z])": r"use \\geqslant",
    r"Mark\s+Essa\s+Sukaiti": "the third author must be absent",
    r"100064482@ku\.ac\.ae": "the third author's email must be absent",
    r"\\(?:textcolor|color)\s*\{red\}": "the primary deep revision is typeset in black",
}

BAD_LOG = (
    "Undefined control sequence",
    "LaTeX Error:",
    "Emergency stop",
    "Fatal error",
    "There were undefined references",
    "There were undefined citations",
    "Citation `",
    "Reference `",
    "Overfull \\hbox",
    "Overfull \\vbox",
)


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=Path)
    parser.add_argument("--reference-audit", type=Path)
    parser.add_argument("tex", type=Path)
    parser.add_argument("bib", type=Path)
    args = parser.parse_args()

    failures: list[str] = []
    sources = [args.tex]
    section_dir = args.tex.parent / "sections"
    if section_dir.is_dir():
        sources.extend(sorted(section_dir.glob("*.tex")))

    labels_by_file: dict[str, list[Path]] = {}
    source_texts: list[str] = []
    for path in sources:
        text = path.read_text(encoding="utf-8")
        source_texts.append(text)
        for pattern, message in FORBIDDEN_SOURCE.items():
            for match in re.finditer(pattern, text):
                failures.append(f"{path}:{line_of(text, match.start())}: {message}")

        for number, line in enumerate(text.splitlines(), start=1):
            if line and not line[0].isspace() and not line.startswith("%") and "  " in line:
                failures.append(f"{path}:{number}: prose contains repeated spaces")
        for label in re.findall(r"\\label\{([^}]+)\}", text):
            labels_by_file.setdefault(label, []).append(path)

    for label, locations in sorted(labels_by_file.items()):
        if len(locations) > 1:
            rendered = ", ".join(str(path) for path in locations)
            failures.append(f"duplicate label {label} in {rendered}")

    main_text = args.tex.read_text(encoding="utf-8")
    if "pdfauthor={Davide Batic and Denys Dutykh}" not in main_text:
        failures.append(f"{args.tex}: expected two-author PDF metadata")
    if not args.bib.is_file() or not args.bib.read_text(encoding="utf-8").strip():
        failures.append(f"{args.bib}: missing or empty bibliography")
        bib_text = ""
    else:
        bib_text = args.bib.read_text(encoding="utf-8")

    bib_keys = re.findall(r"^@[A-Za-z]+\s*\{\s*([^,\s]+)", bib_text, re.MULTILINE)
    duplicate_bib_keys = sorted({key for key in bib_keys if bib_keys.count(key) > 1})
    for key in duplicate_bib_keys:
        failures.append(f"{args.bib}: duplicate BibTeX key {key}")

    combined_sources = "\n".join(source_texts)
    citation_groups = re.findall(
        r"\\cite[A-Za-z*]*\s*(?:\[[^\]]*\]\s*)*\{([^{}]+)\}",
        combined_sources,
    )
    cited_keys = {
        key.strip()
        for group in citation_groups
        for key in group.split(",")
        if key.strip()
    }
    missing_bib_keys = sorted(cited_keys - set(bib_keys))
    for key in missing_bib_keys:
        failures.append(f"citation key {key} is absent from {args.bib}")

    if args.reference_audit:
        if not args.reference_audit.is_file():
            failures.append(f"{args.reference_audit}: reference audit missing")
        else:
            audit_lines = args.reference_audit.read_text(encoding="utf-8").splitlines()
            for key in bib_keys:
                matching = [line for line in audit_lines if f"`{key}`" in line]
                if not matching:
                    failures.append(f"{args.reference_audit}: missing audit row for {key}")
                elif not any("2026-08-25" in line for line in matching):
                    failures.append(
                        f"{args.reference_audit}: audit row for {key} lacks verification date"
                    )

    if args.log:
        if not args.log.is_file():
            failures.append(f"{args.log}: build log missing")
        else:
            log = args.log.read_text(encoding="utf-8", errors="replace")
            for marker in BAD_LOG:
                if marker in log:
                    failures.append(f"{args.log}: contains {marker!r}")

    if failures:
        print("Manuscript checks failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        f"PASS: checked {len(sources)} LaTeX source file(s), {len(cited_keys)} cited keys, "
        f"{len(bib_keys)} audited bibliography records, metadata, and house style."
    )
    if args.log:
        print("PASS: no fatal, undefined-reference, undefined-citation, or overfull-box diagnostics.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
