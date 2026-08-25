#!/usr/bin/env python3
"""Atomic, dependency-free progress tracker for the 2026-08-25 revision.

REVISION_STATE.json is the sole canonical state. REVISION_STATUS.md is a
generated, human-readable resume dashboard. All mutations take an exclusive
file lock and replace both files atomically.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Iterable, Iterator


SCHEMA_VERSION = 1
GATES = (
    "formulation",
    "primary_proof",
    "adversarial_proof",
    "cas_or_computation",
    "literature",
    "manuscript_integration",
    "build_and_render",
)
GATE_ABBREVIATIONS = {
    "formulation": "F",
    "primary_proof": "P1",
    "adversarial_proof": "P2",
    "cas_or_computation": "CAS",
    "literature": "LIT",
    "manuscript_integration": "INT",
    "build_and_render": "BLD",
}
GATE_STATUSES = {"pending", "in_progress", "pass", "fail", "not_applicable"}
WORKFLOWS = {
    "queued",
    "active",
    "blocked",
    "ready_to_integrate",
    "integrated",
    "closed",
    "superseded",
}
PRIORITIES = {"P0", "P1", "P2"}
KINDS = {
    "theorem",
    "lemma",
    "corollary",
    "counterexample",
    "correction",
    "theorem_program",
    "literature_audit",
    "build",
    "figure",
    "code",
    "editorial",
}
PROOF_KINDS = {"theorem", "lemma", "corollary", "counterexample", "theorem_program"}
CLAIM_CLASSES = {
    "unclassified",
    "proved_theorem",
    "exact_identity",
    "counterexample",
    "numerical_observation",
    "asymptotic_evidence",
    "physical_interpretation",
    "conjecture",
    "not_a_scientific_claim",
}
DISPOSITIONS = {
    "proved_as_stated",
    "proved_with_sharper_statement",
    "corrected_and_proved",
    "disproved_with_replacement",
    "exact_identity_verified",
    "evidence_only",
    "withdrawn",
    "superseded",
}
GLOBAL_GATE_NAMES = {
    "ledger_coverage",
    "original_immutable",
    "bibliography_verified",
    "manuscript_claims_classified",
    "code_and_data_verified",
    "figures_tables_inspected",
    "third_author_removed",
    "clean_full_build",
    "page_accounting",
    "release_wording",
}
UNWAIVABLE_GATES = {"formulation", "manuscript_integration", "build_and_render"}
LEDGER_HEADING = re.compile(r"^###\s+((?:COR|THM)-\d+):\s*(.+?)\s*$", re.MULTILINE)
BAD_LOG = re.compile(
    r"LaTeX Error|Package .* Error|Citation .* undefined|Reference .* undefined|"
    r"undefined citations|undefined references|There were undefined|"
    r"multiply[- ]defined|File .* not found|Overfull \\[hv]box",
    re.IGNORECASE,
)


class TrackerError(RuntimeError):
    """A user-correctable tracker error."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_project_path(state_path: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (state_path.parent / path).resolve()


def display_path(state_path: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(state_path.parent.resolve()))
    except ValueError:
        return str(path.resolve())


def load_state(state_path: Path) -> dict[str, Any]:
    try:
        with state_path.open("r", encoding="utf-8") as stream:
            state = json.load(stream)
    except FileNotFoundError as exc:
        raise TrackerError(f"state file does not exist: {state_path}") from exc
    except json.JSONDecodeError as exc:
        raise TrackerError(f"malformed state file {state_path}: {exc}") from exc
    if not isinstance(state, dict):
        raise TrackerError("the state root must be a JSON object")
    return state


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            os.chmod(temporary, path.stat().st_mode & 0o777)
        else:
            os.chmod(temporary, 0o664)
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        with contextlib.suppress(FileNotFoundError):
            temporary.unlink()


@contextlib.contextmanager
def state_lock(state_path: Path) -> Iterator[None]:
    lock_path = state_path.parent / ".revision-state.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def blank_gate_statuses() -> dict[str, str]:
    return {gate: "pending" for gate in GATES}


def new_target(
    target_id: str,
    title: str,
    kind: str,
    priority: str,
    claim_class: str = "unclassified",
    dependencies: Iterable[str] = (),
) -> dict[str, Any]:
    return {
        "id": target_id,
        "title": title,
        "priority": priority,
        "kind": kind,
        "claim_class": claim_class,
        "dependencies": list(dependencies),
        "workflow": "queued",
        "disposition": None,
        "hypotheses_and_scope": "",
        "limitations": "",
        "next_action": "",
        "blocker": None,
        "working_files": [],
        "replacement_target": None,
        "gates": blank_gate_statuses(),
        "gate_records": {},
        "evidence": [],
        "updated_utc": utc_now(),
    }


def parse_ledger(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    return {identifier: title.strip() for identifier, title in LEDGER_HEADING.findall(text)}


def evidence_from_spec(spec: str, state: dict[str, Any], state_path: Path) -> dict[str, Any]:
    project = state["project"]
    if spec.startswith("label:"):
        locator = spec.removeprefix("label:").strip()
        if not locator:
            raise TrackerError("a label evidence specification needs a label name")
        path = resolve_project_path(state_path, project["manuscript_tex"])
        if not path.is_file():
            raise TrackerError(f"manuscript evidence file does not exist: {path}")
        token = rf"\label{{{locator}}}"
        count = path.read_text(encoding="utf-8").count(token)
        if count != 1:
            raise TrackerError(f"expected label {locator!r} exactly once in {path}; found {count}")
        return {
            "path": display_path(state_path, path),
            "role": "manuscript source anchor",
            "locator": locator,
            "fingerprint_mode": "latex_label",
            "fingerprint": locator,
        }
    if spec.startswith("reference:"):
        locator = spec.removeprefix("reference:").strip()
        path = state_path.parent / "REFERENCE_AUDIT.md"
        if not path.is_file():
            raise TrackerError(f"reference audit does not exist: {path}")
        if locator not in path.read_text(encoding="utf-8"):
            raise TrackerError(f"reference anchor {locator!r} was not found in {path}")
        return {
            "path": display_path(state_path, path),
            "role": "verified reference-audit entry",
            "locator": locator,
            "fingerprint_mode": "reference_anchor",
            "fingerprint": locator,
        }
    if spec.startswith("url:"):
        url = spec.removeprefix("url:").strip()
        if not re.match(r"https?://", url):
            raise TrackerError(f"invalid URL evidence: {url!r}")
        return {
            "path": url,
            "role": "authoritative online record",
            "locator": "",
            "fingerprint_mode": "url",
            "fingerprint": url,
        }

    raw_path, separator, locator = spec.partition("#")
    path = resolve_project_path(state_path, raw_path)
    if not path.is_file():
        raise TrackerError(f"evidence file does not exist: {path}")
    return {
        "path": display_path(state_path, path),
        "role": "file evidence",
        "locator": locator if separator else "",
        "fingerprint_mode": "sha256",
        "fingerprint": sha256_file(path),
    }


def check_evidence(
    evidence: dict[str, Any], state_path: Path, errors: list[str], prefix: str
) -> None:
    mode = evidence.get("fingerprint_mode")
    path_value = evidence.get("path", "")
    if mode == "url":
        if not re.match(r"https?://", str(path_value)):
            errors.append(f"{prefix}: malformed URL evidence")
        return
    if mode == "recorded_sha256":
        if not re.fullmatch(r"[0-9a-f]{64}", str(evidence.get("fingerprint", ""))):
            errors.append(f"{prefix}: malformed recorded SHA-256")
        return
    if mode == "recorded_build_digest":
        if not re.fullmatch(r"[0-9a-f]{64}", str(evidence.get("fingerprint", ""))):
            errors.append(f"{prefix}: malformed recorded build digest")
        if not isinstance(evidence.get("files"), list) or not evidence.get("files"):
            errors.append(f"{prefix}: recorded build digest has no dependency list")
        return
    if mode == "build_digest":
        files = evidence.get("files")
        if not isinstance(files, list) or not files:
            errors.append(f"{prefix}: build digest has no dependency file list")
            return
        try:
            current = aggregate_digest(
                [resolve_project_path(state_path, str(item)) for item in files], state_path
            )[0]
        except (OSError, TrackerError) as exc:
            errors.append(f"{prefix}: cannot recompute build digest: {exc}")
            return
        if current != evidence.get("fingerprint"):
            errors.append(f"{prefix}: build dependencies are stale")
        return

    path = resolve_project_path(state_path, str(path_value))
    if not path.is_file():
        errors.append(f"{prefix}: missing evidence file {path_value}")
        return
    if mode == "sha256":
        if sha256_file(path) != evidence.get("fingerprint"):
            errors.append(f"{prefix}: stale evidence checksum for {path_value}")
    elif mode == "latex_label":
        locator = evidence.get("locator", "")
        count = path.read_text(encoding="utf-8").count(rf"\label{{{locator}}}")
        if count != 1:
            errors.append(f"{prefix}: label {locator!r} occurs {count} times")
    elif mode == "reference_anchor":
        locator = evidence.get("locator", "")
        if locator not in path.read_text(encoding="utf-8"):
            errors.append(f"{prefix}: reference anchor {locator!r} is missing")
    else:
        errors.append(f"{prefix}: unknown evidence fingerprint mode {mode!r}")


def gate_is_complete(status: str) -> bool:
    return status in {"pass", "not_applicable"}


def target_closure_errors(target: dict[str, Any], state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    disposition = target.get("disposition")
    if disposition is None:
        errors.append("disposition is not recorded")
    for gate in GATES:
        status = target["gates"].get(gate)
        if not gate_is_complete(status):
            errors.append(f"gate {gate} is {status}")
    if target.get("kind") in PROOF_KINDS:
        for gate in ("formulation", "primary_proof", "adversarial_proof"):
            if target["gates"].get(gate) != "pass":
                errors.append(f"proof-bearing target requires {gate}=pass")
    for gate in UNWAIVABLE_GATES:
        if target["gates"].get(gate) != "pass":
            errors.append(f"every target requires {gate}=pass")
    if target.get("claim_class") == "unclassified":
        errors.append("claim_class remains unclassified")
    for dependency in target.get("dependencies", []):
        other = state.get("targets", {}).get(dependency)
        if other is None:
            errors.append(f"unknown dependency {dependency}")
        elif other.get("workflow") not in {"closed", "superseded"}:
            errors.append(f"dependency {dependency} is not closed")
    if disposition in {"disproved_with_replacement", "superseded"}:
        replacement = target.get("replacement_target")
        if not replacement:
            errors.append(f"{disposition} requires a replacement target")
        elif replacement not in state.get("targets", {}):
            errors.append(f"replacement target {replacement} is unknown")
        elif state["targets"][replacement].get("workflow") not in {"closed", "superseded"}:
            errors.append(f"replacement target {replacement} is not closed")
    return errors


def validate_state(
    state: dict[str, Any],
    state_path: Path,
    strict: bool = False,
    release_complete: bool = False,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if state.get("schema_version") != SCHEMA_VERSION:
        errors.append(
            f"unsupported schema_version {state.get('schema_version')!r}; expected {SCHEMA_VERSION}"
        )
    if not isinstance(state.get("generation"), int) or state.get("generation", -1) < 0:
        errors.append("generation must be a nonnegative integer")
    project = state.get("project")
    if not isinstance(project, dict):
        errors.append("project must be an object")
        project = {}
    targets = state.get("targets")
    if not isinstance(targets, dict):
        errors.append("targets must be an object")
        targets = {}
    for identifier, target in targets.items():
        prefix = f"target {identifier}"
        if not isinstance(target, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if target.get("id") != identifier:
            errors.append(f"{prefix} has mismatched id {target.get('id')!r}")
        if target.get("priority") not in PRIORITIES:
            errors.append(f"{prefix} has invalid priority {target.get('priority')!r}")
        if target.get("kind") not in KINDS:
            errors.append(f"{prefix} has invalid kind {target.get('kind')!r}")
        if target.get("claim_class") not in CLAIM_CLASSES:
            errors.append(f"{prefix} has invalid claim_class {target.get('claim_class')!r}")
        if target.get("workflow") not in WORKFLOWS:
            errors.append(f"{prefix} has invalid workflow {target.get('workflow')!r}")
        if target.get("disposition") not in DISPOSITIONS | {None}:
            errors.append(f"{prefix} has invalid disposition {target.get('disposition')!r}")
        dependencies = target.get("dependencies")
        if not isinstance(dependencies, list):
            errors.append(f"{prefix} dependencies must be a list")
            dependencies = []
        for dependency in dependencies:
            if dependency == identifier:
                errors.append(f"{prefix} depends on itself")
            elif dependency not in targets:
                errors.append(f"{prefix} has unknown dependency {dependency}")
        gates = target.get("gates")
        if not isinstance(gates, dict):
            errors.append(f"{prefix} gates must be an object")
            continue
        missing_gates = set(GATES) - set(gates)
        extra_gates = set(gates) - set(GATES)
        if missing_gates:
            errors.append(f"{prefix} is missing gates: {', '.join(sorted(missing_gates))}")
        if extra_gates:
            errors.append(f"{prefix} has unknown gates: {', '.join(sorted(extra_gates))}")
        records = target.get("gate_records", {})
        if not isinstance(records, dict):
            errors.append(f"{prefix} gate_records must be an object")
            records = {}
        for gate, status in gates.items():
            if status not in GATE_STATUSES:
                errors.append(f"{prefix} gate {gate} has invalid status {status!r}")
                continue
            record = records.get(gate)
            if status in {"pass", "fail", "not_applicable"} and not isinstance(record, dict):
                errors.append(f"{prefix} gate {gate}={status} lacks a record")
                continue
            if status == "not_applicable" and not str(record.get("note", "")).strip():
                errors.append(f"{prefix} gate {gate}=not_applicable lacks a reason")
            if status in {"pass", "fail"}:
                if not str(record.get("method", "")).strip():
                    errors.append(f"{prefix} gate {gate} lacks a method")
                if not str(record.get("checked_by", "")).strip():
                    errors.append(f"{prefix} gate {gate} lacks checked_by")
                evidence = record.get("evidence")
                if not isinstance(evidence, list) or not evidence:
                    errors.append(f"{prefix} gate {gate} lacks evidence")
                elif strict:
                    for index, item in enumerate(evidence, start=1):
                        if not isinstance(item, dict):
                            errors.append(f"{prefix} gate {gate} evidence {index} is not an object")
                        else:
                            check_evidence(item, state_path, errors, f"{prefix} gate {gate}")
        if gates.get("adversarial_proof") == "pass":
            primary = records.get("primary_proof", {})
            adversarial = records.get("adversarial_proof", {})
            if gates.get("primary_proof") != "pass":
                errors.append(f"{prefix} adversarial proof passed before the primary proof")
            same_method = str(primary.get("method", "")).strip().casefold() == str(
                adversarial.get("method", "")
            ).strip().casefold()
            same_checker = str(primary.get("checked_by", "")).strip().casefold() == str(
                adversarial.get("checked_by", "")
            ).strip().casefold()
            if same_method and same_checker:
                errors.append(
                    f"{prefix} adversarial proof must differ in method or checker from the primary proof"
                )
        if target.get("workflow") in {"closed", "superseded"}:
            errors.extend(f"{prefix}: {item}" for item in target_closure_errors(target, state))
        if target.get("workflow") == "blocked" and not str(target.get("blocker", "")).strip():
            errors.append(f"{prefix} is blocked without a blocker")
        if target.get("workflow") not in {"closed", "superseded"} and not target.get("next_action"):
            warnings.append(f"{prefix} has no next action")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identifier: str, chain: list[str]) -> None:
        if identifier in visiting:
            start = chain.index(identifier) if identifier in chain else 0
            errors.append("dependency cycle: " + " -> ".join(chain[start:] + [identifier]))
            return
        if identifier in visited:
            return
        visiting.add(identifier)
        for dependency in targets.get(identifier, {}).get("dependencies", []):
            if dependency in targets:
                visit(dependency, chain + [identifier])
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in targets:
        visit(identifier, [])

    global_gates = state.get("global_gates")
    if not isinstance(global_gates, dict):
        errors.append("global_gates must be an object")
        global_gates = {}
    missing_global = GLOBAL_GATE_NAMES - set(global_gates)
    if missing_global:
        errors.append(f"missing global gates: {', '.join(sorted(missing_global))}")
    for name, gate in global_gates.items():
        if not isinstance(gate, dict) or gate.get("status") not in GATE_STATUSES:
            errors.append(f"global gate {name} is malformed")
            continue
        status = gate.get("status")
        if status in {"pass", "fail"}:
            if not str(gate.get("method", "")).strip():
                errors.append(f"global gate {name} lacks a method")
            if not str(gate.get("checked_by", "")).strip():
                errors.append(f"global gate {name} lacks checked_by")
            evidence = gate.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                errors.append(f"global gate {name} lacks evidence")
            elif strict:
                for item in evidence:
                    if not isinstance(item, dict):
                        errors.append(f"global gate {name} has malformed evidence")
                    else:
                        check_evidence(item, state_path, errors, f"global gate {name}")
        if status == "not_applicable" and not str(gate.get("note", "")).strip():
            errors.append(f"global gate {name}=not_applicable lacks a reason")

    session = state.get("session")
    if not isinstance(session, dict):
        errors.append("session must be an object")
    else:
        active = session.get("active_target")
        if active is not None and active not in targets:
            errors.append(f"session refers to unknown active target {active}")

    if strict and project:
        ledger_value = project.get("ledger_path")
        original_value = project.get("original_tex_path")
        if ledger_value:
            ledger_path = resolve_project_path(state_path, ledger_value)
            if not ledger_path.is_file():
                errors.append(f"ledger does not exist: {ledger_path}")
            else:
                ledger_hash = sha256_file(ledger_path)
                if ledger_hash != project.get("ledger_sha256"):
                    errors.append("ledger hash changed; inspect it and run sync-ledger explicitly")
                required = parse_ledger(ledger_path)
                missing = sorted(set(required) - set(targets))
                if missing:
                    errors.append(f"ledger targets missing from state: {', '.join(missing)}")
        if original_value:
            original_path = resolve_project_path(state_path, original_value)
            if not original_path.is_file():
                errors.append(f"archival original does not exist: {original_path}")
            elif sha256_file(original_path) != project.get("original_tex_sha256"):
                errors.append("archival original hash changed")
    if release_complete:
        for identifier, target in targets.items():
            if target.get("workflow") not in {"closed", "superseded"}:
                errors.append(
                    f"release incomplete: target {identifier} has workflow "
                    f"{target.get('workflow')}"
                )
        for name, gate in global_gates.items():
            if not gate_is_complete(gate.get("status", "pending")):
                errors.append(
                    f"release incomplete: global gate {name} is "
                    f"{gate.get('status')}"
                )
        if session.get("active_target") is not None:
            errors.append("release incomplete: an active target remains")
        if not session.get("last_known_good_build"):
            errors.append("release incomplete: no clean build has been recorded")
    return errors, warnings


def target_gate_summary(target: dict[str, Any]) -> str:
    symbols = {
        "pending": "·",
        "in_progress": "~",
        "pass": "✓",
        "fail": "✗",
        "not_applicable": "–",
    }
    return " ".join(
        f"{GATE_ABBREVIATIONS[name]}:{symbols.get(target['gates'].get(name), '?')}"
        for name in GATES
    )


def safe_markdown(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def render_status(state: dict[str, Any], state_path: Path) -> str:
    session = state["session"]
    targets = state["targets"]
    active = session.get("active_target")
    workflows: dict[str, int] = {name: 0 for name in WORKFLOWS}
    for target in targets.values():
        workflows[target["workflow"]] = workflows.get(target["workflow"], 0) + 1
    closed = workflows.get("closed", 0) + workflows.get("superseded", 0)
    last_build = session.get("last_known_good_build")
    lines = [
        "<!-- Generated from REVISION_STATE.json; do not edit. -->",
        f"<!-- generation: {state['generation']} -->",
        "# Revision status: read this first when resuming",
        "",
        f"- State generation: `{state['generation']}`",
        f"- Updated (UTC): `{state['updated_utc']}`",
        f"- Closed targets: `{closed}/{len(targets)}`",
        f"- Active target: `{active or 'none'}`",
        f"- Next action: {safe_markdown(session.get('next_action') or 'Select a P0 target and record it with `begin`.')}",
    ]
    blockers = session.get("blockers") or []
    lines.append(f"- Blockers: {safe_markdown('; '.join(blockers) if blockers else 'none')}")
    if last_build:
        lines.extend(
            [
                f"- Last good build: `{last_build.get('pdf', '')}`; "
                f"{last_build.get('pages', '?')} pages; SHA-256 `{last_build.get('pdf_sha256', '')}`",
                f"- Page delta from the 37-page baseline: `{last_build.get('page_delta', '?'):+d}`"
                if isinstance(last_build.get("page_delta"), int)
                else "- Page delta from the 37-page baseline: `unknown`",
            ]
        )
    else:
        lines.append("- Last good build: none recorded")
    working = session.get("working_files") or []
    lines.append(f"- Files in flight: {safe_markdown(', '.join(working) if working else 'none')}")
    lines.extend(
        [
            "",
            "Gate legend: `F` formulation, `P1` primary proof, `P2` adversarial proof, "
            "`CAS` symbolic/numerical check, `LIT` literature, `INT` manuscript integration, "
            "`BLD` build/render. Symbols are `✓` pass, `–` justified not applicable, "
            "`~` in progress, `✗` failed, and `·` pending.",
            "",
            "## Target dashboard",
            "",
            "| Target | Priority | Workflow | Gates | Next action |",
            "|---|---:|---|---|---|",
        ]
    )
    for identifier in sorted(targets, key=lambda item: (targets[item]["priority"], item)):
        target = targets[identifier]
        lines.append(
            f"| {safe_markdown(identifier)} | {safe_markdown(target['priority'])} | "
            f"{safe_markdown(target['workflow'])} | {safe_markdown(target_gate_summary(target))} | "
            f"{safe_markdown(target.get('next_action', ''))} |"
        )
    lines.extend(["", "## Recent checkpoints", ""])
    history = state.get("history", [])[-8:]
    if history:
        for entry in reversed(history):
            target_text = f" `{entry['target']}`" if entry.get("target") else ""
            lines.append(
                f"- `{entry.get('updated_utc', '')}`{target_text}: "
                f"{safe_markdown(entry.get('summary', ''))}"
            )
    else:
        lines.append("- No checkpoint has yet been recorded.")
    lines.extend(
        [
            "",
            "## Global acceptance gates",
            "",
            "| Gate | Status | Note |",
            "|---|---|---|",
        ]
    )
    for name, gate in state["global_gates"].items():
        lines.append(
            f"| {safe_markdown(name)} | {safe_markdown(gate.get('status', ''))} | "
            f"{safe_markdown(gate.get('note', ''))} |"
        )
    lines.extend(
        [
            "",
            "## Resume commands",
            "",
            "```bash",
            "python3 codes/revision_tracker.py validate --strict",
            "python3 codes/revision_tracker.py resume",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def commit_state(
    state: dict[str, Any],
    state_path: Path,
    action: str,
    summary: str,
    target: str | None,
    actor: str,
) -> None:
    now = utc_now()
    state["generation"] += 1
    state["updated_utc"] = now
    state.setdefault("history", []).append(
        {
            "generation": state["generation"],
            "updated_utc": now,
            "actor": actor,
            "action": action,
            "target": target,
            "summary": summary.strip(),
        }
    )
    errors, _ = validate_state(state, state_path, strict=False)
    if errors:
        raise TrackerError("refusing to write invalid state:\n- " + "\n- ".join(errors))
    state_text = json.dumps(state, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
    atomic_write(state_path, state_text)
    status_path = state_path.parent / "REVISION_STATUS.md"
    atomic_write(status_path, render_status(state, state_path))


def get_target(state: dict[str, Any], identifier: str) -> dict[str, Any]:
    try:
        return state["targets"][identifier]
    except KeyError as exc:
        raise TrackerError(f"unknown target {identifier!r}") from exc


def update_derived_workflow(target: dict[str, Any]) -> None:
    if target["workflow"] in {"closed", "superseded", "blocked"}:
        return
    early = (
        "formulation",
        "primary_proof",
        "adversarial_proof",
        "cas_or_computation",
        "literature",
    )
    if all(gate_is_complete(target["gates"][name]) for name in early):
        if target["gates"]["manuscript_integration"] == "pending":
            target["workflow"] = "ready_to_integrate"
        elif gate_is_complete(target["gates"]["manuscript_integration"]):
            target["workflow"] = "integrated"
        else:
            target["workflow"] = "active"
    else:
        target["workflow"] = "active"


def print_target(target: dict[str, Any]) -> None:
    print(f"{target['id']} — {target['title']}")
    print(
        f"priority={target['priority']} kind={target['kind']} "
        f"workflow={target['workflow']} claim_class={target['claim_class']}"
    )
    if target.get("disposition"):
        print(f"disposition={target['disposition']}")
    for gate in GATES:
        status = target["gates"][gate]
        record = target.get("gate_records", {}).get(gate, {})
        detail = record.get("note") or record.get("method") or ""
        print(f"  {gate:24s} {status:14s} {detail}")
    print(f"next: {target.get('next_action') or 'not recorded'}")
    if target.get("blocker"):
        print(f"blocker: {target['blocker']}")
    if target.get("working_files"):
        print("working files: " + ", ".join(target["working_files"]))


def command_status(args: argparse.Namespace) -> int:
    state_path = args.state.resolve()
    state = load_state(state_path)
    if args.target:
        print_target(get_target(state, args.target))
        return 0
    counts: dict[str, int] = {}
    for target in state["targets"].values():
        counts[target["workflow"]] = counts.get(target["workflow"], 0) + 1
    print(
        f"Revision generation {state['generation']} ({state['updated_utc']}); "
        f"{len(state['targets'])} targets"
    )
    print("; ".join(f"{name}={counts[name]}" for name in sorted(counts)))
    active = state["session"].get("active_target")
    print(f"active={active or 'none'}")
    print(f"next={state['session'].get('next_action') or 'not recorded'}")
    return 0


def command_resume(args: argparse.Namespace) -> int:
    state_path = args.state.resolve()
    state = load_state(state_path)
    errors, warnings = validate_state(state, state_path, strict=True)
    print(f"Revision generation {state['generation']} — updated {state['updated_utc']}")
    if errors:
        print("VALIDATION ERRORS:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Validation: PASS (schema, ledger coverage/hash, original hash, and recorded evidence)")
    if warnings:
        print(f"Advisories: {len(warnings)} queued targets do not yet have target-local next actions")
    session = state["session"]
    active = session.get("active_target")
    if active:
        print()
        print_target(get_target(state, active))
    else:
        print("Active target: none")
    blockers = session.get("blockers") or []
    print("Session blockers: " + ("; ".join(blockers) if blockers else "none"))
    print("Files in flight: " + (", ".join(session.get("working_files") or []) or "none"))
    print("Exact next action: " + (session.get("next_action") or "select a P0 target and run begin"))
    last_build = session.get("last_known_good_build")
    if last_build:
        print(
            f"Last good build: {last_build['pdf']} — {last_build['pages']} pages "
            f"(delta {last_build['page_delta']:+d}), SHA-256 {last_build['pdf_sha256']}"
        )
    else:
        print("Last good build: none recorded; archival baseline is 37 pages")
    open_targets = [
        item for item in state["targets"].values() if item["workflow"] not in {"closed", "superseded"}
    ]
    for priority in ("P0", "P1", "P2"):
        group = [item for item in open_targets if item["priority"] == priority]
        if group:
            print(f"Open {priority}: " + ", ".join(item["id"] for item in group))
    history = state.get("history", [])[-5:]
    if history:
        print("Recent checkpoints:")
        for entry in reversed(history):
            label = f" {entry['target']}" if entry.get("target") else ""
            print(f"  - {entry['updated_utc']}{label}: {entry['summary']}")
    unfinished_global = [
        name
        for name, gate in state["global_gates"].items()
        if gate.get("status") not in {"pass", "not_applicable"}
    ]
    print(
        "Open global gates: "
        + (", ".join(unfinished_global) if unfinished_global else "none")
    )
    return 2 if errors else 0


def command_begin(args: argparse.Namespace) -> int:
    state_path = args.state.resolve()
    with state_lock(state_path):
        state = load_state(state_path)
        target = get_target(state, args.target)
        if target["workflow"] in {"closed", "superseded"} and not args.reopen:
            raise TrackerError(f"{args.target} is closed; pass --reopen to resume it explicitly")
        if args.reopen:
            target["disposition"] = None
            target["replacement_target"] = None
        target["workflow"] = "active"
        target["blocker"] = None
        target["next_action"] = args.next.strip()
        target["working_files"] = list(dict.fromkeys(args.working_file or []))
        target["updated_utc"] = utc_now()
        state["session"].update(
            {
                "active_target": args.target,
                "next_action": args.next.strip(),
                "blockers": [],
                "working_files": target["working_files"],
            }
        )
        commit_state(
            state,
            state_path,
            "begin",
            f"Began {args.target}. Next: {args.next.strip()}",
            args.target,
            args.actor,
        )
    print(f"Began {args.target}; generation {state['generation']}")
    return 0


def command_gate(args: argparse.Namespace) -> int:
    state_path = args.state.resolve()
    with state_lock(state_path):
        state = load_state(state_path)
        target = get_target(state, args.target)
        if args.gate not in GATES:
            raise TrackerError(f"unknown gate {args.gate!r}")
        if target["workflow"] in {"closed", "superseded"}:
            raise TrackerError(f"{args.target} is closed; reopen it before changing a gate")
        if args.status in {"pass", "fail"}:
            if not args.method or not args.checked_by:
                raise TrackerError("pass/fail requires --method and --checked-by")
            if not args.evidence:
                raise TrackerError("pass/fail requires at least one --evidence item")
            evidence = [evidence_from_spec(item, state, state_path) for item in args.evidence]
            if args.gate == "build_and_render" and args.status == "pass":
                raise TrackerError(
                    "record build_and_render=pass with record-build so the PDF, log, dependency digest, "
                    "page count, and visual-inspection note are captured"
                )
            if args.gate == "literature" and args.status == "pass" and not any(
                item.get("fingerprint_mode") == "reference_anchor" for item in evidence
            ):
                raise TrackerError(
                    "literature=pass requires at least one reference:ANCHOR evidence item from REFERENCE_AUDIT.md"
                )
            record = {
                "status": args.status,
                "method": args.method.strip(),
                "checked_by": args.checked_by.strip(),
                "checked_utc": utc_now(),
                "evidence": evidence,
                "note": (args.note or "").strip(),
            }
            if args.gate == "adversarial_proof" and args.status == "pass":
                if target["gates"]["primary_proof"] != "pass":
                    raise TrackerError("the primary proof must pass before the adversarial proof")
                primary = target.get("gate_records", {}).get("primary_proof", {})
                same_method = primary.get("method", "").strip().casefold() == args.method.strip().casefold()
                same_checker = primary.get("checked_by", "").strip().casefold() == args.checked_by.strip().casefold()
                if same_method and same_checker:
                    raise TrackerError(
                        "the adversarial proof must use a different method or a different checker"
                    )
        elif args.status == "not_applicable":
            reason = (args.reason or args.note or "").strip()
            if not reason:
                raise TrackerError("not_applicable requires --reason")
            if args.gate in UNWAIVABLE_GATES:
                raise TrackerError(f"{args.gate} cannot be waived for any target")
            if args.gate in {"primary_proof", "adversarial_proof"} and target["kind"] in PROOF_KINDS:
                raise TrackerError(f"{args.gate} cannot be waived for proof-bearing target {args.target}")
            record = {
                "status": args.status,
                "method": "not applicable",
                "checked_by": args.checked_by or args.actor,
                "checked_utc": utc_now(),
                "evidence": [],
                "note": reason,
            }
        elif args.status == "in_progress":
            record = {
                "status": args.status,
                "method": (args.method or "").strip(),
                "checked_by": (args.checked_by or args.actor).strip(),
                "checked_utc": utc_now(),
                "evidence": [],
                "note": (args.note or "").strip(),
            }
        else:  # pending reset
            record = None

        target["gates"][args.gate] = args.status
        if record is None:
            target.setdefault("gate_records", {}).pop(args.gate, None)
        else:
            target.setdefault("gate_records", {})[args.gate] = record
        target["updated_utc"] = utc_now()
        update_derived_workflow(target)
        summary = f"Set {args.gate}={args.status}"
        if args.note:
            summary += f": {args.note.strip()}"
        commit_state(state, state_path, "gate", summary, args.target, args.actor)
    print(f"{args.target} {args.gate}={args.status}; generation {state['generation']}")
    return 0


def command_checkpoint(args: argparse.Namespace) -> int:
    state_path = args.state.resolve()
    with state_lock(state_path):
        state = load_state(state_path)
        target = get_target(state, args.target)
        closed = target["workflow"] in {"closed", "superseded"}
        next_action = (args.next or "").strip()
        if not closed and not next_action:
            raise TrackerError("a nonclosed checkpoint requires a nonempty --next action")
        blocker = (args.blocker or "").strip() or None
        if blocker:
            target["workflow"] = "blocked"
        elif not closed:
            update_derived_workflow(target)
        target["blocker"] = blocker
        target["next_action"] = next_action
        if args.working_file:
            target["working_files"] = list(dict.fromkeys(args.working_file))
        target["updated_utc"] = utc_now()
        state["session"].update(
            {
                "active_target": None if closed else args.target,
                "next_action": next_action,
                "blockers": [blocker] if blocker else [],
                "working_files": target.get("working_files", []),
            }
        )
        commit_state(
            state,
            state_path,
            "checkpoint",
            args.summary.strip(),
            args.target,
            args.actor,
        )
    print(f"Checkpointed {args.target}; generation {state['generation']}")
    return 0


def command_close(args: argparse.Namespace) -> int:
    state_path = args.state.resolve()
    with state_lock(state_path):
        state = load_state(state_path)
        target = get_target(state, args.target)
        target["claim_class"] = args.claim_class
        target["disposition"] = args.disposition
        if args.replacement_target:
            if args.replacement_target not in state["targets"]:
                raise TrackerError(f"unknown replacement target {args.replacement_target}")
            target["replacement_target"] = args.replacement_target
        if args.disposition in {"disproved_with_replacement", "superseded"}:
            replacement = target.get("replacement_target")
            if not replacement:
                raise TrackerError(f"{args.disposition} requires --replacement-target")
            if state["targets"][replacement]["workflow"] not in {"closed", "superseded"}:
                raise TrackerError(f"replacement target {replacement} is not closed")
        closure_errors = target_closure_errors(target, state)
        if closure_errors:
            raise TrackerError("cannot close target:\n- " + "\n- ".join(closure_errors))
        target["workflow"] = "superseded" if args.disposition == "superseded" else "closed"
        target["next_action"] = ""
        target["blocker"] = None
        target["updated_utc"] = utc_now()
        if state["session"].get("active_target") == args.target:
            state["session"].update(
                {
                    "active_target": None,
                    "next_action": "Select the next unresolved P0 or P1 target.",
                    "blockers": [],
                    "working_files": [],
                }
            )
        commit_state(
            state,
            state_path,
            "close",
            f"Closed with disposition {args.disposition}.",
            args.target,
            args.actor,
        )
    print(f"Closed {args.target}; generation {state['generation']}")
    return 0


def command_add_target(args: argparse.Namespace) -> int:
    state_path = args.state.resolve()
    with state_lock(state_path):
        state = load_state(state_path)
        if args.target in state["targets"]:
            raise TrackerError(f"target {args.target} already exists")
        for dependency in args.depends_on or []:
            if dependency not in state["targets"]:
                raise TrackerError(f"unknown dependency {dependency}")
        target = new_target(
            args.target,
            args.title.strip(),
            args.kind,
            args.priority,
            args.claim_class,
            args.depends_on or [],
        )
        target["next_action"] = (args.next or "").strip()
        state["targets"][args.target] = target
        commit_state(
            state,
            state_path,
            "add-target",
            f"Added {args.target}: {args.title.strip()}",
            args.target,
            args.actor,
        )
    print(f"Added {args.target}; generation {state['generation']}")
    return 0


def command_sync_ledger(args: argparse.Namespace) -> int:
    state_path = args.state.resolve()
    if args.check:
        state = load_state(state_path)
        ledger_path = resolve_project_path(state_path, state["project"]["ledger_path"])
        actual = parse_ledger(ledger_path)
        missing = sorted(set(actual) - set(state["targets"]))
        hash_matches = sha256_file(ledger_path) == state["project"].get("ledger_sha256")
        if missing or not hash_matches:
            if missing:
                print("Missing ledger targets: " + ", ".join(missing), file=sys.stderr)
            if not hash_matches:
                print("Ledger hash differs from the recorded hash.", file=sys.stderr)
            return 2
        print(f"Ledger sync check: PASS ({len(actual)} COR/THM targets; hash matches)")
        return 0

    with state_lock(state_path):
        state = load_state(state_path)
        ledger_path = resolve_project_path(state_path, state["project"]["ledger_path"])
        actual = parse_ledger(ledger_path)
        added: list[str] = []
        for identifier, title in actual.items():
            if identifier not in state["targets"]:
                kind = "correction" if identifier.startswith("COR-") else "theorem"
                state["targets"][identifier] = new_target(identifier, title, kind, "P1")
                added.append(identifier)
        state["project"]["ledger_sha256"] = sha256_file(ledger_path)
        summary = "Synchronized ledger hash"
        if added:
            summary += "; added " + ", ".join(added)
        commit_state(state, state_path, "sync-ledger", summary, None, args.actor)
    print(f"Ledger synchronized; added {len(added)} target(s); generation {state['generation']}")
    return 0


def command_global_gate(args: argparse.Namespace) -> int:
    state_path = args.state.resolve()
    with state_lock(state_path):
        state = load_state(state_path)
        if args.status in {"pass", "fail"}:
            if not args.method or not args.checked_by:
                raise TrackerError("pass/fail requires --method and --checked-by")
            if not args.evidence:
                raise TrackerError("pass/fail requires at least one --evidence item")
            evidence = [evidence_from_spec(item, state, state_path) for item in args.evidence]
            record = {
                "status": args.status,
                "method": args.method.strip(),
                "checked_by": args.checked_by.strip(),
                "checked_utc": utc_now(),
                "evidence": evidence,
                "note": (args.note or "").strip(),
            }
        elif args.status == "not_applicable":
            reason = (args.reason or args.note or "").strip()
            if not reason:
                raise TrackerError("not_applicable requires --reason")
            if args.name in {
                "ledger_coverage",
                "original_immutable",
                "bibliography_verified",
                "manuscript_claims_classified",
                "third_author_removed",
                "clean_full_build",
                "page_accounting",
            }:
                raise TrackerError(f"global gate {args.name} cannot be waived")
            record = {
                "status": args.status,
                "method": "not applicable",
                "checked_by": args.checked_by or args.actor,
                "checked_utc": utc_now(),
                "evidence": [],
                "note": reason,
            }
        elif args.status == "in_progress":
            record = {
                "status": args.status,
                "method": (args.method or "").strip(),
                "checked_by": (args.checked_by or args.actor).strip(),
                "checked_utc": utc_now(),
                "evidence": [],
                "note": (args.note or "").strip(),
            }
        else:
            record = {
                "status": "pending",
                "method": "",
                "checked_by": "",
                "checked_utc": None,
                "evidence": [],
                "note": (args.note or "").strip(),
            }
        state["global_gates"][args.name] = record
        commit_state(
            state,
            state_path,
            "global-gate",
            f"Set global gate {args.name}={args.status}.",
            None,
            args.actor,
        )
    print(f"global {args.name}={args.status}; generation {state['generation']}")
    return 0


def aggregate_digest(paths: Iterable[Path], state_path: Path) -> tuple[str, list[str]]:
    unique = sorted({path.resolve() for path in paths}, key=lambda item: str(item))
    if not unique:
        raise TrackerError("cannot compute an aggregate digest over no files")
    digest = hashlib.sha256()
    displayed: list[str] = []
    for path in unique:
        if not path.is_file():
            raise TrackerError(f"build dependency is missing: {path}")
        relative = display_path(state_path, path)
        displayed.append(relative)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest(), displayed


def pdf_pages(path: Path) -> int:
    try:
        result = subprocess.run(
            ["pdfinfo", str(path)],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise TrackerError("pdfinfo is required to record the PDF page count") from exc
    except subprocess.CalledProcessError as exc:
        raise TrackerError(f"pdfinfo failed: {exc.stderr.strip()}") from exc
    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.MULTILINE)
    if not match:
        raise TrackerError("pdfinfo did not report a page count")
    return int(match.group(1))


def command_record_build(args: argparse.Namespace) -> int:
    state_path = args.state.resolve()
    with state_lock(state_path):
        state = load_state(state_path)
        project = state["project"]
        pdf = resolve_project_path(state_path, args.pdf or project["manuscript_pdf"])
        log = resolve_project_path(
            state_path,
            args.log or str(Path(project["manuscript_tex"]).with_suffix(".log")),
        )
        if not pdf.is_file():
            raise TrackerError(f"PDF does not exist: {pdf}")
        if not log.is_file():
            raise TrackerError(f"build log does not exist: {log}")
        log_text = log.read_text(encoding="utf-8", errors="replace")
        diagnostics = sorted(set(match.group(0) for match in BAD_LOG.finditer(log_text)))
        if diagnostics:
            raise TrackerError("substantive build diagnostics found: " + "; ".join(diagnostics))
        dependency_paths = [
            resolve_project_path(state_path, project["manuscript_tex"]),
            resolve_project_path(state_path, project["manuscript_bib"]),
        ]
        sections = state_path.parent / "sections"
        if sections.is_dir():
            dependency_paths.extend(path for path in sections.rglob("*.tex") if path.is_file())
        figures = state_path.parent / "figures"
        if figures.is_dir():
            dependency_paths.extend(path for path in figures.rglob("*") if path.is_file())
        build_digest, build_files = aggregate_digest(dependency_paths, state_path)
        pages = pdf_pages(pdf)
        pdf_hash = sha256_file(pdf)
        baseline = int(project["baseline_pdf_pages"])
        record = {
            "pdf": display_path(state_path, pdf),
            "pdf_sha256": pdf_hash,
            "pages": pages,
            "baseline_pages": baseline,
            "page_delta": pages - baseline,
            "log_sha256": sha256_file(log),
            "build_digest": build_digest,
            "build_files": build_files,
            "recorded_utc": utc_now(),
            "inspection_note": args.inspection_note.strip(),
        }
        state["session"]["last_known_good_build"] = record
        historical = args.target is not None
        evidence = [
            {
                "path": display_path(state_path, pdf),
                "role": "compiled manuscript PDF",
                "locator": "",
                "fingerprint_mode": "recorded_sha256" if historical else "sha256",
                "fingerprint": pdf_hash,
            },
            {
                "path": display_path(state_path, log),
                "role": "clean LaTeX build log retained by digest",
                "locator": "",
                "fingerprint_mode": "recorded_sha256",
                "fingerprint": record["log_sha256"],
            },
            {
                "path": "",
                "role": "aggregate manuscript dependency digest",
                "locator": "",
                "fingerprint_mode": "recorded_build_digest" if historical else "build_digest",
                "fingerprint": build_digest,
                "files": build_files,
            },
        ]
        gate_record = {
            "status": "pass",
            "method": "clean LaTeX/BibTeX build with diagnostic scan and pdfinfo page count",
            "checked_by": args.actor,
            "checked_utc": utc_now(),
            "evidence": evidence,
            "note": (
                f"{pages} pages; delta {pages - baseline:+d} from the 37-page baseline. "
                f"Reading-size inspection: {args.inspection_note.strip()}"
            ),
        }
        if args.target:
            target = get_target(state, args.target)
            if target["workflow"] in {"closed", "superseded"}:
                raise TrackerError(f"{args.target} is closed; reopen before replacing its build gate")
            target["gates"]["build_and_render"] = "pass"
            target.setdefault("gate_records", {})["build_and_render"] = gate_record
            target["updated_utc"] = utc_now()
            update_derived_workflow(target)
        else:
            state["global_gates"]["clean_full_build"] = gate_record.copy()
            state["global_gates"]["page_accounting"] = {
                **gate_record,
                "method": "pdfinfo page count compared with frozen archival baseline",
            }
        commit_state(
            state,
            state_path,
            "record-build",
            f"Recorded clean {pages}-page build (delta {pages - baseline:+d}).",
            args.target,
            args.actor,
        )
    print(
        f"Recorded {pages}-page build for {args.target or 'global acceptance'}; "
        f"generation {state['generation']}"
    )
    return 0


def command_validate(args: argparse.Namespace) -> int:
    state_path = args.state.resolve()
    state = load_state(state_path)
    errors, warnings = validate_state(
        state,
        state_path,
        strict=args.strict,
        release_complete=args.release_complete,
    )
    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        mode = "strict" if args.strict else "structural"
        if args.release_complete:
            mode += ", release-complete"
        print(f"Validation: PASS ({mode}; generation {state['generation']})")
    if warnings and args.show_warnings:
        print(f"Advisories ({len(warnings)}):")
        for warning in warnings:
            print(f"- {warning}")
    return 2 if errors else 0


def command_render(args: argparse.Namespace) -> int:
    state_path = args.state.resolve()
    with state_lock(state_path):
        state = load_state(state_path)
        errors, _ = validate_state(state, state_path, strict=False)
        if errors:
            raise TrackerError("cannot render invalid state:\n- " + "\n- ".join(errors))
        status = render_status(state, state_path)
        if args.stdout:
            print(status, end="")
        else:
            status_path = state_path.parent / "REVISION_STATUS.md"
            atomic_write(status_path, status)
            print(f"Rendered {status_path} from generation {state['generation']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    default_state = Path(__file__).resolve().parent.parent / "REVISION_STATE.json"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--state", type=Path, default=default_state, help="canonical state file (default: revised/REVISION_STATE.json)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="show compact progress or one target")
    status.add_argument("target", nargs="?")
    status.set_defaults(func=command_status)

    resume = subparsers.add_parser("resume", help="validate and print an exact restart handoff")
    resume.set_defaults(func=command_resume)

    begin = subparsers.add_parser("begin", help="select an active target")
    begin.add_argument("target")
    begin.add_argument("--next", required=True)
    begin.add_argument("--working-file", action="append", default=[])
    begin.add_argument("--reopen", action="store_true")
    begin.add_argument("--actor", default="root")
    begin.set_defaults(func=command_begin)

    gate = subparsers.add_parser("gate", help="record one scientific gate")
    gate.add_argument("target")
    gate.add_argument("gate", choices=GATES)
    gate.add_argument("status", choices=sorted(GATE_STATUSES))
    gate.add_argument("--method")
    gate.add_argument("--checked-by")
    gate.add_argument("--evidence", action="append", default=[])
    gate.add_argument("--note")
    gate.add_argument("--reason")
    gate.add_argument("--actor", default="root")
    gate.set_defaults(func=command_gate)

    checkpoint = subparsers.add_parser("checkpoint", help="record a safe session boundary")
    checkpoint.add_argument("target")
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--next")
    checkpoint.add_argument("--working-file", action="append", default=[])
    checkpoint.add_argument("--blocker")
    checkpoint.add_argument("--actor", default="root")
    checkpoint.set_defaults(func=command_checkpoint)

    close = subparsers.add_parser("close", help="close a target only after all gates pass")
    close.add_argument("target")
    close.add_argument("--disposition", required=True, choices=sorted(DISPOSITIONS))
    close.add_argument("--claim-class", required=True, choices=sorted(CLAIM_CLASSES - {"unclassified"}))
    close.add_argument("--replacement-target")
    close.add_argument("--actor", default="root")
    close.set_defaults(func=command_close)

    add = subparsers.add_parser("add-target", help="add a newly discovered result or task")
    add.add_argument("target")
    add.add_argument("--title", required=True)
    add.add_argument("--kind", required=True, choices=sorted(KINDS))
    add.add_argument("--priority", required=True, choices=sorted(PRIORITIES))
    add.add_argument("--claim-class", default="unclassified", choices=sorted(CLAIM_CLASSES))
    add.add_argument("--depends-on", action="append", default=[])
    add.add_argument("--next")
    add.add_argument("--actor", default="root")
    add.set_defaults(func=command_add_target)

    sync = subparsers.add_parser("sync-ledger", help="check or explicitly accept ledger changes")
    sync.add_argument("--check", action="store_true")
    sync.add_argument("--actor", default="root")
    sync.set_defaults(func=command_sync_ledger)

    global_gate = subparsers.add_parser("global-gate", help="record one global acceptance gate")
    global_gate.add_argument("name", choices=sorted(GLOBAL_GATE_NAMES))
    global_gate.add_argument("status", choices=sorted(GATE_STATUSES))
    global_gate.add_argument("--method")
    global_gate.add_argument("--checked-by")
    global_gate.add_argument("--evidence", action="append", default=[])
    global_gate.add_argument("--note")
    global_gate.add_argument("--reason")
    global_gate.add_argument("--actor", default="root")
    global_gate.set_defaults(func=command_global_gate)

    validate = subparsers.add_parser("validate", help="validate schema and recorded evidence")
    validate.add_argument("--strict", action="store_true")
    validate.add_argument(
        "--release-complete",
        action="store_true",
        help="also require every target and global gate to be complete",
    )
    validate.add_argument("--show-warnings", action="store_true")
    validate.set_defaults(func=command_validate)

    render = subparsers.add_parser("render", help="regenerate the Markdown dashboard")
    render.add_argument("--stdout", action="store_true")
    render.set_defaults(func=command_render)

    build = subparsers.add_parser("record-build", help="record a clean PDF build and page count")
    build.add_argument("--target")
    build.add_argument("--pdf")
    build.add_argument("--log")
    build.add_argument(
        "--inspection-note",
        required=True,
        help="pages/figures inspected at intended reading size and the observed result",
    )
    build.add_argument("--actor", default="root")
    build.set_defaults(func=command_record_build)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except TrackerError as exc:
        print(f"revision_tracker: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"revision_tracker: operating-system error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("revision_tracker: interrupted; the previous atomic state remains valid", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
