#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".next",
    ".nuxt",
    ".turbo",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "target",
    "__pycache__",
}

TEXT_SUFFIXES = {
    ".js",
    ".cjs",
    ".mjs",
    ".ts",
    ".tsx",
    ".jsx",
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".xml",
    ".gradle",
    ".kts",
    ".rb",
    ".php",
    ".swift",
    ".html",
    ".htm",
    ".env",
    "",
}

HIGH_RISK_PERMISSIONS = {
    "<all_urls>": "Broad host access across all websites.",
    "debugger": "Can inspect and control other pages and tabs.",
    "nativeMessaging": "Can communicate with native executables.",
    "proxy": "Can intercept or modify network routing.",
    "webRequestBlocking": "Can block or modify browser requests.",
}

MEDIUM_RISK_PERMISSIONS = {
    "cookies": "Can read and change cookies.",
    "clipboardRead": "Can read clipboard content.",
    "clipboardWrite": "Can write clipboard content.",
    "downloads": "Can download files to disk.",
    "history": "Can inspect browsing history.",
    "management": "Can inspect or control installed extensions.",
    "scripting": "Can inject code into pages.",
    "tabs": "Can inspect or modify browser tabs.",
    "webRequest": "Can observe browser requests.",
}

SUSPICIOUS_SCRIPT_PATTERNS = (
    (re.compile(r"curl\b.*\|\s*(sh|bash)\b", re.IGNORECASE), "Downloads and pipes remote content into a shell."),
    (re.compile(r"wget\b.*\|\s*(sh|bash)\b", re.IGNORECASE), "Downloads and pipes remote content into a shell."),
    (re.compile(r"invoke-webrequest\b.*iex\b", re.IGNORECASE), "Downloads and immediately executes PowerShell content."),
    (re.compile(r"\beval\s*\(", re.IGNORECASE), "Uses eval, which can hide dynamic code execution."),
    (re.compile(r"\bnew Function\s*\(", re.IGNORECASE), "Uses Function constructor for dynamic code execution."),
    (re.compile(r"child_process\.(exec|spawn)\b", re.IGNORECASE), "Starts subprocesses from application code."),
    (re.compile(r"base64[^\\n]{0,80}(decode|atob)", re.IGNORECASE), "Decodes base64 content that may hide payloads."),
)

URL_DEP_RE = re.compile(r"(git\+|https?://|ssh://|git@)", re.IGNORECASE)
GITHUB_ACTION_RE = re.compile(r"uses:\s*([^\s#]+)")
GITHUB_ACTION_PIN_RE = re.compile(r"^[0-9a-fA-F]{40}$")
PACKAGE_LOCK_VERSION_RE = re.compile(r"^(.*)@([^@].*)$")
YARN_KEY_RE = re.compile(r'^"?([^":]+(?:,[^":]+)*)"?\:\s*$')
YARN_VERSION_RE = re.compile(r'^\s{2}version\s+"([^"]+)"\s*$')
YARN_RESOLVED_RE = re.compile(r'^\s{2}resolved\s+"([^"]+)"\s*$')
YARN_INTEGRITY_RE = re.compile(r'^\s{2}integrity\s+(.+)$')
DOCKER_FROM_RE = re.compile(r"^\s*FROM(?:\s+--platform=\S+)?\s+([^\s]+)", re.IGNORECASE)
DOCKER_ADD_URL_RE = re.compile(r"^\s*ADD\s+(https?://\S+)", re.IGNORECASE)
DOCKER_USER_RE = re.compile(r"^\s*USER\s+([^\s]+)", re.IGNORECASE)
COMPOSE_IMAGE_RE = re.compile(r"^\s*image:\s*['\"]?([^'\"\s]+)['\"]?\s*$", re.IGNORECASE)
COMPOSE_PRIVILEGED_RE = re.compile(r"^\s*privileged:\s*true\s*$", re.IGNORECASE)
COMPOSE_NETWORK_HOST_RE = re.compile(r"^\s*network_mode:\s*['\"]?host['\"]?\s*$", re.IGNORECASE)
COMPOSE_PID_HOST_RE = re.compile(r"^\s*pid:\s*['\"]?host['\"]?\s*$", re.IGNORECASE)
COMPOSE_USER_RE = re.compile(r"^\s*user:\s*['\"]?([^'\"\s]+)['\"]?\s*$", re.IGNORECASE)
COMPOSE_VOLUME_RE = re.compile(r"^\s*-\s*['\"]?([^'\"\n]+)['\"]?\s*$")
TRUSTED_REGISTRY_HOSTS = (
    "registry.npmjs.org/",
    "registry.yarnpkg.com/",
    "registry.npmjs.com/",
    "repo.maven.apache.org/",
    "files.pythonhosted.org/",
)
REQ_LINE_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*([<>=!~].*)?$")
GEM_RE = re.compile(r'^\s*gem\s+["\']([^"\']+)["\'](?:\s*,\s*["\']([^"\']+)["\'])?')
GO_REQUIRE_RE = re.compile(r"^\s*([^\s]+)\s+([^\s]+)\s*$")
GRADLE_DEP_RE = re.compile(
    r'^\s*(implementation|api|compileOnly|runtimeOnly|testImplementation|classpath)\s*\(?\s*["\']([^"\']+)["\']'
)
SWIFT_PACKAGE_RE = re.compile(
    r'\.package\s*\(\s*url:\s*"([^"]+)"(?:\s*,\s*(?:from|exact):\s*"([^"]+)")?',
    re.IGNORECASE,
)
BASE64_BLOB_RE = re.compile(r"[A-Za-z0-9+/]{200,}={0,2}")


@dataclass
class InventoryItem:
    category: str
    ecosystem: str
    name: str
    version: str
    source_file: str
    source_type: str = "registry"
    notes: list[str] = field(default_factory=list)


@dataclass
class Finding:
    severity: str
    title: str
    file: str
    evidence: str
    recommendation: str
    line: int | None = None
    related: list[str] = field(default_factory=list)


@dataclass
class FileScanResult:
    path: str
    findings: list[Finding] = field(default_factory=list)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def iter_files(root: Path) -> Iterable[Path]:
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        base = Path(current_root)
        for name in files:
            yield base / name


def iter_directories(root: Path) -> Iterable[Path]:
    for current_root, dirs, _files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        yield Path(current_root)


def add_inventory(
    items: list[InventoryItem],
    category: str,
    ecosystem: str,
    name: str,
    version: str,
    source_file: str,
    source_type_override: str | None = None,
) -> None:
    source_type = source_type_override or ("direct-url" if URL_DEP_RE.search(version) else "registry")
    notes = []
    if source_type == "direct-url":
        notes.append("Pinned to a direct URL or VCS source instead of a package registry.")
    items.append(
        InventoryItem(
            category=category,
            ecosystem=ecosystem,
            name=name,
            version=version or "unspecified",
            source_file=source_file,
            source_type=source_type,
            notes=notes,
        )
    )


def render_structured_dependency(value: object) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)


def has_structured_direct_source(value: object) -> bool:
    if isinstance(value, str):
        return bool(URL_DEP_RE.search(value))
    if isinstance(value, dict):
        direct_keys = {"git", "url", "path", "rev", "tag", "branch"}
        return any(key in value for key in direct_keys)
    return False


def structured_source_note(value: object) -> str:
    if isinstance(value, dict):
        parts = []
        for key in ("git", "url", "path", "rev", "tag", "branch"):
            if key in value:
                parts.append(f"{key}={value[key]}")
        if parts:
            return ", ".join(parts)
    return str(value)


def add_finding(
    findings: list[Finding],
    severity: str,
    title: str,
    file: str,
    evidence: str,
    recommendation: str,
    related: list[str] | None = None,
    line: int | None = None,
) -> None:
    findings.append(
        Finding(
            severity=severity,
            title=title,
            file=file,
            evidence=evidence,
            recommendation=recommendation,
            related=related or [],
            line=line,
        )
    )


def is_unusual_resolved_source(value: str) -> bool:
    lowered = value.lower()
    if lowered.startswith("git+") or lowered.startswith("git@") or lowered.startswith("ssh://"):
        return True
    if lowered.startswith("http://") or lowered.startswith("https://"):
        return not any(host in lowered for host in TRUSTED_REGISTRY_HOSTS)
    return False


def parse_container_image_reference(image: str) -> tuple[str, str]:
    if "@" in image:
        name, digest = image.rsplit("@", 1)
        return name, f"@{digest}"
    last_segment = image.rsplit("/", 1)[-1]
    if ":" in last_segment:
        name, tag = image.rsplit(":", 1)
        return name, tag
    return image, "latest-or-unspecified"


def image_version_is_floating(version: str) -> bool:
    return version in {"latest", "latest-or-unspecified"}


def parse_package_json(path: Path, root: Path, items: list[InventoryItem], findings: list[Finding]) -> None:
    data = json.loads(read_text(path))
    rel_path = rel(path, root)

    for key in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
        deps = data.get(key, {})
        if isinstance(deps, dict):
            for name, version in deps.items():
                add_inventory(items, "dependency", f"npm:{key}", name, str(version), rel_path)
                if URL_DEP_RE.search(str(version)):
                    findings.append(
                        Finding(
                            severity="medium",
                            title="Direct npm dependency source",
                            file=rel_path,
                            evidence=f"{name} is installed from {version}.",
                            recommendation="Verify ownership, integrity, and why a registry release is not used.",
                            related=[name],
                        )
                    )

    scripts = data.get("scripts", {})
    if isinstance(scripts, dict):
        for script_name in ("preinstall", "install", "postinstall", "prepare", "prepublish", "postpack"):
            command = scripts.get(script_name)
            if not isinstance(command, str):
                continue
            for pattern, explanation in SUSPICIOUS_SCRIPT_PATTERNS:
                if pattern.search(command):
                    findings.append(
                        Finding(
                            severity="high" if "pipe" in explanation or "PowerShell" in explanation else "medium",
                            title=f"Suspicious npm lifecycle script: {script_name}",
                            file=rel_path,
                            evidence=f"{script_name}: {command}",
                            recommendation="Review whether this lifecycle hook is required and lock down the package source.",
                            related=[script_name],
                        )
                    )
                    break

    if isinstance(data.get("engines"), dict) and "vscode" in data["engines"]:
        add_inventory(
            items,
            "extension",
            "vscode",
            data.get("name", path.parent.name),
            str(data["engines"]["vscode"]),
            rel_path,
        )


def parse_package_lock_dependency(
    dep_name: str,
    entry: object,
    ecosystem: str,
    rel_path: str,
    items: list[InventoryItem],
    findings: list[Finding],
) -> None:
    if not isinstance(entry, dict):
        return
    version = str(entry.get("version", "unspecified"))
    resolved = str(entry.get("resolved", "") or "")
    integrity = str(entry.get("integrity", "") or "")
    rendered = version
    if resolved:
        rendered = f"{version} ({resolved})"
    source_type = "direct-url" if resolved and is_unusual_resolved_source(resolved) else "registry"
    add_inventory(items, "dependency", ecosystem, dep_name, rendered, rel_path, source_type)
    if resolved and source_type == "direct-url":
        related = [dep_name]
        if integrity:
            related.append(integrity)
        add_finding(
            findings,
            "medium",
            "Direct npm lockfile source",
            rel_path,
            f"{dep_name}: {resolved}",
            "Confirm the resolved artifact is expected and comes from a trusted registry or repository.",
            related=related,
        )


def parse_package_lock(path: Path, root: Path, items: list[InventoryItem], findings: list[Finding]) -> None:
    data = json.loads(read_text(path))
    rel_path = rel(path, root)

    packages = data.get("packages", {})
    if isinstance(packages, dict):
        for package_path, entry in packages.items():
            if not isinstance(entry, dict) or package_path == "":
                continue
            dep_name = package_path.split("node_modules/")[-1]
            if dep_name:
                parse_package_lock_dependency(dep_name, entry, "npm-lock", rel_path, items, findings)

    dependencies = data.get("dependencies", {})
    if isinstance(dependencies, dict):
        for dep_name, entry in dependencies.items():
            parse_package_lock_dependency(dep_name, entry, "npm-lock", rel_path, items, findings)


def parse_requirements(path: Path, root: Path, items: list[InventoryItem], findings: list[Finding]) -> None:
    rel_path = rel(path, root)
    for raw_line in read_text(path).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-r"):
            continue
        if URL_DEP_RE.search(line) or " @ " in line:
            name = line.split("@", 1)[0].strip().split("[", 1)[0]
            add_inventory(items, "dependency", "python", name or line, line, rel_path)
            findings.append(
                Finding(
                    severity="medium",
                    title="Direct Python dependency source",
                    file=rel_path,
                    evidence=line,
                    recommendation="Confirm the package source is trusted and pinned to a specific commit or release.",
                    related=[name or line],
                )
            )
            continue
        match = REQ_LINE_RE.match(line)
        if match:
            add_inventory(items, "dependency", "python", match.group(1), match.group(2) or "unspecified", rel_path)


def parse_pyproject(path: Path, root: Path, items: list[InventoryItem], findings: list[Finding]) -> None:
    if tomllib is None:
        return
    data = tomllib.loads(read_text(path))
    rel_path = rel(path, root)

    project = data.get("project", {})
    dependencies = project.get("dependencies", [])
    for entry in dependencies:
        name = entry.split()[0]
        add_inventory(items, "dependency", "python", name, entry, rel_path)
        if URL_DEP_RE.search(entry):
            findings.append(
                Finding(
                    severity="medium",
                    title="Direct Python dependency source",
                    file=rel_path,
                    evidence=entry,
                    recommendation="Verify the upstream repository or archive is trusted and pinned.",
                    related=[name],
                )
            )
    optional = project.get("optional-dependencies", {})
    if isinstance(optional, dict):
        for group, values in optional.items():
            for entry in values:
                name = entry.split()[0]
                add_inventory(items, "dependency", f"python:{group}", name, entry, rel_path)

    poetry = data.get("tool", {}).get("poetry", {})
    poetry_deps = poetry.get("dependencies", {})
    if isinstance(poetry_deps, dict):
        for name, version in poetry_deps.items():
            if name == "python":
                continue
            rendered = render_structured_dependency(version)
            add_inventory(items, "dependency", "poetry", name, rendered, rel_path)
            if has_structured_direct_source(version):
                findings.append(
                    Finding(
                        severity="medium",
                        title="Direct Poetry dependency source",
                        file=rel_path,
                        evidence=f"{name}: {structured_source_note(version)}",
                        recommendation="Verify the upstream source is expected and pinned tightly enough for your risk tolerance.",
                        related=[name],
                    )
                )


def parse_cargo_toml(path: Path, root: Path, items: list[InventoryItem], findings: list[Finding]) -> None:
    if tomllib is None:
        return
    data = tomllib.loads(read_text(path))
    rel_path = rel(path, root)
    for section in ("dependencies", "dev-dependencies", "build-dependencies"):
        deps = data.get(section, {})
        if isinstance(deps, dict):
            for name, version in deps.items():
                rendered = render_structured_dependency(version)
                add_inventory(items, "dependency", f"cargo:{section}", name, rendered, rel_path)
                if has_structured_direct_source(version):
                    findings.append(
                        Finding(
                            severity="medium",
                            title="Direct Cargo dependency source",
                            file=rel_path,
                            evidence=f"{name}: {structured_source_note(version)}",
                            recommendation="Confirm the repository or path dependency is intentional and pinned to a trusted revision.",
                            related=[name],
                        )
                    )


def parse_cargo_lock(path: Path, root: Path, items: list[InventoryItem]) -> None:
    if tomllib is None:
        return
    data = tomllib.loads(read_text(path))
    rel_path = rel(path, root)
    packages = data.get("package", [])
    if not isinstance(packages, list):
        return
    for package in packages:
        if not isinstance(package, dict):
            continue
        name = str(package.get("name", "")).strip()
        version = str(package.get("version", "unspecified")).strip()
        if name:
            add_inventory(items, "dependency", "cargo-lock", name, version or "unspecified", rel_path)


def parse_go_mod(path: Path, root: Path, items: list[InventoryItem]) -> None:
    rel_path = rel(path, root)
    in_require_block = False
    for raw_line in read_text(path).splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("require ("):
            in_require_block = True
            continue
        if in_require_block and stripped == ")":
            in_require_block = False
            continue
        if stripped.startswith("require "):
            stripped = stripped[len("require ") :]
        if not in_require_block and raw_line == stripped and not raw_line.startswith("require "):
            continue
        if stripped.startswith("//") or not stripped:
            continue
        match = GO_REQUIRE_RE.match(stripped)
        if match:
            add_inventory(items, "dependency", "go", match.group(1), match.group(2), rel_path)


def parse_gemfile(path: Path, root: Path, items: list[InventoryItem]) -> None:
    rel_path = rel(path, root)
    for raw_line in read_text(path).splitlines():
        match = GEM_RE.match(raw_line)
        if match:
            add_inventory(items, "dependency", "ruby", match.group(1), match.group(2) or "unspecified", rel_path)


def parse_gemfile_lock(path: Path, root: Path, items: list[InventoryItem]) -> None:
    rel_path = rel(path, root)
    section = ""
    in_specs = False
    for raw_line in read_text(path).splitlines():
        if not raw_line.strip():
            continue
        if raw_line == raw_line.strip():
            section = raw_line.rstrip(":")
            in_specs = False
            continue
        if section != "GEM":
            continue
        if raw_line.startswith("  specs:"):
            in_specs = True
            continue
        if not in_specs:
            continue
        match = re.match(r"^\s{4}([A-Za-z0-9_.-]+)\s+\(([^)]+)\)", raw_line)
        if match:
            add_inventory(items, "dependency", "bundler-lock", match.group(1), match.group(2), rel_path)


def parse_composer(path: Path, root: Path, items: list[InventoryItem]) -> None:
    data = json.loads(read_text(path))
    rel_path = rel(path, root)
    for key in ("require", "require-dev"):
        deps = data.get(key, {})
        if isinstance(deps, dict):
            for name, version in deps.items():
                add_inventory(items, "dependency", f"composer:{key}", name, str(version), rel_path)


def parse_pom_xml(path: Path, root: Path, items: list[InventoryItem]) -> None:
    rel_path = rel(path, root)
    try:
        xml_root = ET.fromstring(read_text(path))
    except ET.ParseError:
        return
    ns_prefix = ""
    if xml_root.tag.startswith("{"):
        ns_prefix = xml_root.tag.split("}", 1)[0] + "}"
    for dep in xml_root.findall(f".//{ns_prefix}dependency"):
        group_id = dep.findtext(f"{ns_prefix}groupId", default="").strip()
        artifact_id = dep.findtext(f"{ns_prefix}artifactId", default="").strip()
        version = dep.findtext(f"{ns_prefix}version", default="unspecified").strip()
        if artifact_id:
            name = f"{group_id}:{artifact_id}" if group_id else artifact_id
            add_inventory(items, "dependency", "maven", name, version, rel_path)


def parse_csproj(path: Path, root: Path, items: list[InventoryItem]) -> None:
    rel_path = rel(path, root)
    try:
        xml_root = ET.fromstring(read_text(path))
    except ET.ParseError:
        return
    ns_prefix = ""
    if xml_root.tag.startswith("{"):
        ns_prefix = xml_root.tag.split("}", 1)[0] + "}"
    for dep in xml_root.findall(f".//{ns_prefix}PackageReference"):
        name = (dep.attrib.get("Include") or dep.attrib.get("Update") or "").strip()
        version = (dep.attrib.get("Version") or dep.findtext(f"{ns_prefix}Version", default="unspecified")).strip()
        if name:
            add_inventory(items, "dependency", "nuget", name, version or "unspecified", rel_path)


def parse_packages_config(path: Path, root: Path, items: list[InventoryItem]) -> None:
    rel_path = rel(path, root)
    try:
        xml_root = ET.fromstring(read_text(path))
    except ET.ParseError:
        return
    for dep in xml_root.findall(".//package"):
        name = dep.attrib.get("id", "").strip()
        version = dep.attrib.get("version", "unspecified").strip()
        if name:
            add_inventory(items, "dependency", "nuget", name, version, rel_path)


def parse_gradle(path: Path, root: Path, items: list[InventoryItem]) -> None:
    rel_path = rel(path, root)
    for raw_line in read_text(path).splitlines():
        match = GRADLE_DEP_RE.match(raw_line)
        if match:
            add_inventory(items, "dependency", f"gradle:{match.group(1)}", match.group(2), "declared", rel_path)


def parse_poetry_lock(path: Path, root: Path, items: list[InventoryItem], findings: list[Finding]) -> None:
    if tomllib is None:
        return
    data = tomllib.loads(read_text(path))
    rel_path = rel(path, root)
    packages = data.get("package", [])
    if not isinstance(packages, list):
        return
    for package in packages:
        if not isinstance(package, dict):
            continue
        name = str(package.get("name", "")).strip()
        version = str(package.get("version", "unspecified")).strip()
        if not name:
            continue
        source = package.get("source")
        rendered = version
        if isinstance(source, dict):
            rendered = f"{version} ({json.dumps(source, sort_keys=True)})"
        source_type = "direct-url" if has_structured_direct_source(source) else "registry"
        add_inventory(items, "dependency", "poetry-lock", name, rendered, rel_path, source_type)
        if source_type == "direct-url":
            add_finding(
                findings,
                "medium",
                "Direct Poetry lockfile source",
                rel_path,
                f"{name}: {structured_source_note(source)}",
                "Confirm the locked source is trusted and pinned to the intended revision or artifact.",
                related=[name],
            )


def parse_pnpm_lock(path: Path, root: Path, items: list[InventoryItem], findings: list[Finding]) -> None:
    rel_path = rel(path, root)
    for raw_line in read_text(path).splitlines():
        stripped = raw_line.strip()
        if not stripped.startswith("/"):
            continue
        package_ref = stripped.rstrip(":").split("(", 1)[0]
        body = package_ref[1:]
        if "@" not in body:
            continue
        name, version = body.rsplit("@", 1)
        source_type = "direct-url" if is_unusual_resolved_source(version) else "registry"
        add_inventory(items, "dependency", "pnpm-lock", name, version or "unspecified", rel_path, source_type)
        if source_type == "direct-url":
            add_finding(
                findings,
                "medium",
                "Direct pnpm lockfile source",
                rel_path,
                f"{name}: {version}",
                "Confirm the locked source is expected and comes from a trusted location.",
                related=[name],
            )


def parse_yarn_lock(path: Path, root: Path, items: list[InventoryItem], findings: list[Finding]) -> None:
    rel_path = rel(path, root)
    current_names: list[str] = []
    current_version: str | None = None
    current_resolved: str | None = None
    current_integrity: str | None = None

    def flush() -> None:
        nonlocal current_names, current_version, current_resolved, current_integrity
        if not current_names or not current_version:
            current_names = []
            current_version = None
            current_resolved = None
            current_integrity = None
            return
        for name in current_names:
            rendered = current_version
            if current_resolved:
                rendered = f"{current_version} ({current_resolved})"
            source_type = "direct-url" if current_resolved and is_unusual_resolved_source(current_resolved) else "registry"
            add_inventory(items, "dependency", "yarn-lock", name, rendered, rel_path, source_type)
            if source_type == "direct-url":
                related = [name]
                if current_integrity:
                    related.append(current_integrity)
                add_finding(
                    findings,
                    "medium",
                    "Direct Yarn lockfile source",
                    rel_path,
                    f"{name}: {current_resolved}",
                    "Confirm the locked tarball or repository URL is expected and trusted.",
                    related=related,
                )
        current_names = []
        current_version = None
        current_resolved = None
        current_integrity = None

    for raw_line in read_text(path).splitlines():
        key_match = YARN_KEY_RE.match(raw_line)
        if key_match:
            flush()
            selectors = [selector.strip().strip('"') for selector in key_match.group(1).split(",")]
            names = []
            for selector in selectors:
                match = PACKAGE_LOCK_VERSION_RE.match(selector)
                names.append(match.group(1) if match else selector)
            current_names = sorted(set(name for name in names if name))
            continue
        version_match = YARN_VERSION_RE.match(raw_line)
        if version_match:
            current_version = version_match.group(1)
            continue
        resolved_match = YARN_RESOLVED_RE.match(raw_line)
        if resolved_match:
            current_resolved = resolved_match.group(1)
            continue
        integrity_match = YARN_INTEGRITY_RE.match(raw_line)
        if integrity_match:
            current_integrity = integrity_match.group(1).strip()
    flush()


def parse_swift_package(path: Path, root: Path, items: list[InventoryItem], findings: list[Finding]) -> None:
    rel_path = rel(path, root)
    for raw_line in read_text(path).splitlines():
        match = SWIFT_PACKAGE_RE.search(raw_line)
        if match:
            url = match.group(1)
            version = match.group(2) or "unspecified"
            name = Path(url.rstrip("/")).stem or url
            add_inventory(items, "dependency", "swiftpm", name, version, rel_path)
            findings.append(
                Finding(
                    severity="medium",
                    title="Swift package uses direct repository source",
                    file=rel_path,
                    evidence=url,
                    recommendation="Confirm the repository owner is expected and pin to an exact revision for sensitive systems.",
                    related=[name],
                )
            )


def parse_browser_manifest(path: Path, root: Path, items: list[InventoryItem], findings: list[Finding]) -> None:
    data = json.loads(read_text(path))
    if "manifest_version" not in data:
        return
    rel_path = rel(path, root)
    name = str(data.get("name", path.parent.name))
    version = str(data.get("version", "unspecified"))
    add_inventory(items, "extension", "browser-extension", name, version, rel_path)

    permissions = []
    for key in ("permissions", "optional_permissions", "host_permissions"):
        values = data.get(key, [])
        if isinstance(values, list):
            permissions.extend(str(v) for v in values)

    for perm in permissions:
        if perm in HIGH_RISK_PERMISSIONS:
            findings.append(
                Finding(
                    severity="high",
                    title=f"High-risk browser extension permission: {perm}",
                    file=rel_path,
                    evidence=HIGH_RISK_PERMISSIONS[perm],
                    recommendation="Confirm the permission is necessary and document the user-visible behavior it enables.",
                    related=[name],
                )
            )
        elif perm in MEDIUM_RISK_PERMISSIONS:
            findings.append(
                Finding(
                    severity="medium",
                    title=f"Sensitive browser extension permission: {perm}",
                    file=rel_path,
                    evidence=MEDIUM_RISK_PERMISSIONS[perm],
                    recommendation="Review whether the permission can be narrowed or removed.",
                    related=[name],
                )
            )


def parse_jetbrains_plugin(path: Path, root: Path, items: list[InventoryItem]) -> None:
    rel_path = rel(path, root)
    try:
        xml_root = ET.fromstring(read_text(path))
    except ET.ParseError:
        return
    name = xml_root.findtext("name", default=path.parent.name).strip()
    version = xml_root.findtext("version", default="unspecified").strip()
    add_inventory(items, "extension", "jetbrains-plugin", name, version, rel_path)


def parse_github_workflow(path: Path, root: Path, items: list[InventoryItem], findings: list[Finding]) -> None:
    rel_path = rel(path, root)
    for number, raw_line in enumerate(read_text(path).splitlines(), start=1):
        match = GITHUB_ACTION_RE.search(raw_line)
        if not match:
            continue
        action_ref = match.group(1).strip().strip("\"'")
        if action_ref.startswith("./") or action_ref.startswith("docker://"):
            continue
        if "@" not in action_ref:
            continue
        name, ref_name = action_ref.rsplit("@", 1)
        add_inventory(items, "automation", "github-action", name, ref_name, rel_path)
        if not GITHUB_ACTION_PIN_RE.fullmatch(ref_name):
            findings.append(
                Finding(
                    severity="medium",
                    title="GitHub Action not pinned to a commit SHA",
                    file=rel_path,
                    line=number,
                    evidence=action_ref,
                    recommendation="Pin third-party actions to a full commit SHA and review upstream ownership.",
                    related=[name],
                )
            )


def parse_dockerfile(path: Path, root: Path, items: list[InventoryItem], findings: list[Finding]) -> None:
    rel_path = rel(path, root)
    for number, raw_line in enumerate(read_text(path).splitlines(), start=1):
        from_match = DOCKER_FROM_RE.match(raw_line)
        if from_match:
            image = from_match.group(1)
            name, version = parse_container_image_reference(image)
            add_inventory(items, "container-image", "docker", name, version, rel_path)
            if image_version_is_floating(version):
                add_finding(
                    findings,
                    "medium",
                    "Docker base image is not pinned",
                    rel_path,
                    image,
                    "Pin the base image to a specific tag or digest so builds remain reproducible and reviewable.",
                    related=[name],
                    line=number,
                )
            continue

        add_match = DOCKER_ADD_URL_RE.match(raw_line)
        if add_match:
            add_finding(
                findings,
                "medium",
                "Dockerfile downloads remote content with ADD",
                rel_path,
                add_match.group(1),
                "Prefer fetching remote artifacts explicitly with integrity checks, or vendor the file into the build context.",
                line=number,
            )
            continue

        user_match = DOCKER_USER_RE.match(raw_line)
        if user_match and user_match.group(1).lower() in {"root", "0"}:
            add_finding(
                findings,
                "medium",
                "Container runs as root",
                rel_path,
                raw_line.strip(),
                "Use a non-root runtime user unless the container genuinely requires elevated privileges.",
                line=number,
            )


def parse_compose_file(path: Path, root: Path, items: list[InventoryItem], findings: list[Finding]) -> None:
    rel_path = rel(path, root)
    for number, raw_line in enumerate(read_text(path).splitlines(), start=1):
        image_match = COMPOSE_IMAGE_RE.match(raw_line)
        if image_match:
            image = image_match.group(1)
            name, version = parse_container_image_reference(image)
            add_inventory(items, "container-image", "docker-compose", name, version, rel_path)
            if image_version_is_floating(version):
                add_finding(
                    findings,
                    "medium",
                    "Compose image is not pinned",
                    rel_path,
                    image,
                    "Pin the image to a specific tag or digest so deployments remain reproducible and easier to review.",
                    related=[name],
                    line=number,
                )
            continue

        if COMPOSE_PRIVILEGED_RE.match(raw_line):
            add_finding(
                findings,
                "high",
                "Compose service runs privileged",
                rel_path,
                raw_line.strip(),
                "Remove privileged mode unless the service cannot function without broad host access.",
                line=number,
            )
            continue

        if COMPOSE_NETWORK_HOST_RE.match(raw_line):
            add_finding(
                findings,
                "medium",
                "Compose service uses host networking",
                rel_path,
                raw_line.strip(),
                "Review whether host networking is necessary, since it bypasses normal container network isolation.",
                line=number,
            )
            continue

        if COMPOSE_PID_HOST_RE.match(raw_line):
            add_finding(
                findings,
                "medium",
                "Compose service shares host PID namespace",
                rel_path,
                raw_line.strip(),
                "Avoid sharing the host PID namespace unless process inspection across the host is required.",
                line=number,
            )
            continue

        user_match = COMPOSE_USER_RE.match(raw_line)
        if user_match and user_match.group(1).lower() in {"root", "0"}:
            add_finding(
                findings,
                "medium",
                "Compose service runs as root",
                rel_path,
                raw_line.strip(),
                "Use a non-root runtime user unless the service genuinely requires it.",
                line=number,
            )
            continue

        volume_match = COMPOSE_VOLUME_RE.match(raw_line)
        if volume_match:
            volume = volume_match.group(1).strip()
            if "/var/run/docker.sock" in volume:
                add_finding(
                    findings,
                    "high",
                    "Compose service mounts the Docker socket",
                    rel_path,
                    volume,
                    "Treat Docker socket access as host-level control and avoid mounting it unless absolutely necessary.",
                    line=number,
                )
            elif volume.startswith("/:") or volume == "/":
                add_finding(
                    findings,
                    "high",
                    "Compose service mounts the host root filesystem",
                    rel_path,
                    volume,
                    "Avoid exposing the host root filesystem to containers unless you have a tightly controlled operational need.",
                    line=number,
                )


def scan_text_file(path: Path, root: Path, findings: list[Finding]) -> None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return
    rel_path = rel(path, root)
    text = read_text(path)
    for number, line in enumerate(text.splitlines(), start=1):
        if "re.compile(" in line:
            continue
        for pattern, explanation in SUSPICIOUS_SCRIPT_PATTERNS:
            if pattern.search(line):
                findings.append(
                    Finding(
                        severity="high" if "pipe" in explanation or "PowerShell" in explanation else "medium",
                        title="Suspicious code pattern",
                        file=rel_path,
                        line=number,
                        evidence=line.strip()[:300],
                        recommendation=explanation,
                    )
                )
                break
        if BASE64_BLOB_RE.search(line):
            findings.append(
                Finding(
                    severity="low",
                    title="Large encoded blob in source",
                    file=rel_path,
                    line=number,
                    evidence="Found a long base64-like string.",
                    recommendation="Confirm this is expected binary data and not an embedded payload or secret.",
                )
            )


def dedupe_inventory(items: list[InventoryItem]) -> list[InventoryItem]:
    seen = set()
    deduped = []
    for item in items:
        key = (item.category, item.ecosystem, item.name, item.version, item.source_file)
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return sorted(deduped, key=lambda item: (item.category, item.ecosystem, item.name.lower(), item.source_file))


def dedupe_findings(findings: list[Finding]) -> list[Finding]:
    severity_order = {"high": 0, "medium": 1, "low": 2}
    seen = set()
    deduped = []
    for finding in findings:
        key = (finding.severity, finding.title, finding.file, finding.line, finding.evidence)
        if key not in seen:
            seen.add(key)
            deduped.append(finding)
    return sorted(deduped, key=lambda f: (severity_order.get(f.severity, 9), f.file, f.line or 0, f.title))


def scan(root: Path) -> dict:
    inventory: list[InventoryItem] = []
    findings: list[Finding] = []
    scanned_directories = sorted(rel(path, root) for path in iter_directories(root))
    scanned_paths: list[str] = []

    for path in iter_files(root):
        rel_path = rel(path, root)
        scanned_paths.append(rel_path)
        name = path.name

        try:
            if name == "package.json":
                parse_package_json(path, root, inventory, findings)
            elif name == "package-lock.json":
                parse_package_lock(path, root, inventory, findings)
            elif name.startswith("requirements") and path.suffix == ".txt":
                parse_requirements(path, root, inventory, findings)
            elif name == "pyproject.toml":
                parse_pyproject(path, root, inventory, findings)
            elif name == "poetry.lock":
                parse_poetry_lock(path, root, inventory, findings)
            elif name == "Cargo.toml":
                parse_cargo_toml(path, root, inventory, findings)
            elif name == "Cargo.lock":
                parse_cargo_lock(path, root, inventory)
            elif name == "go.mod":
                parse_go_mod(path, root, inventory)
            elif name == "Gemfile":
                parse_gemfile(path, root, inventory)
            elif name == "Gemfile.lock":
                parse_gemfile_lock(path, root, inventory)
            elif name == "pnpm-lock.yaml":
                parse_pnpm_lock(path, root, inventory, findings)
            elif name == "yarn.lock":
                parse_yarn_lock(path, root, inventory, findings)
            elif name == "composer.json":
                parse_composer(path, root, inventory)
            elif name == "pom.xml":
                parse_pom_xml(path, root, inventory)
            elif path.suffix == ".csproj":
                parse_csproj(path, root, inventory)
            elif name == "packages.config":
                parse_packages_config(path, root, inventory)
            elif name in {"build.gradle", "build.gradle.kts"}:
                parse_gradle(path, root, inventory)
            elif name == "Package.swift":
                parse_swift_package(path, root, inventory, findings)
            elif name == "manifest.json":
                parse_browser_manifest(path, root, inventory, findings)
            elif name == "plugin.xml":
                parse_jetbrains_plugin(path, root, inventory)
            elif path.parts[-3:-1] == (".github", "workflows") and path.suffix in {".yml", ".yaml"}:
                parse_github_workflow(path, root, inventory, findings)
            elif name == "Dockerfile" or name.startswith("Dockerfile."):
                parse_dockerfile(path, root, inventory, findings)
            elif name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}:
                parse_compose_file(path, root, inventory, findings)
        except Exception as exc:
            findings.append(
                Finding(
                    severity="low",
                    title="Failed to parse file",
                    file=rel_path,
                    evidence=str(exc),
                    recommendation="Open the file manually if it is relevant to the system inventory.",
                )
            )

        scan_text_file(path, root, findings)

    inventory = dedupe_inventory(inventory)
    findings = dedupe_findings(findings)

    findings_by_file: dict[str, list[Finding]] = {}
    for finding in findings:
        findings_by_file.setdefault(finding.file, []).append(finding)

    file_results = [
        asdict(FileScanResult(path=path, findings=findings_by_file.get(path, [])))
        for path in sorted(scanned_paths)
    ]

    counts = {"high": 0, "medium": 0, "low": 0}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1

    return {
        "root": str(root),
        "scanned_directories": scanned_directories,
        "scanned_files": len(scanned_paths),
        "file_results": file_results,
        "inventory": [asdict(item) for item in inventory],
        "findings": [asdict(finding) for finding in findings],
        "summary": {
            "directories_scanned": len(scanned_directories),
            "third_party_items": len(inventory),
            "extensions_and_addons": sum(1 for item in inventory if item.category == "extension"),
            "high_findings": counts["high"],
            "medium_findings": counts["medium"],
            "low_findings": counts["low"],
        },
    }


def render_text(report: dict) -> str:
    lines = []
    summary = report["summary"]
    flagged_files = [file_result for file_result in report["file_results"] if file_result["findings"]]
    clean_files = [file_result for file_result in report["file_results"] if not file_result["findings"]]
    lines.append("Security Scan Summary")
    lines.append(f"Root: {report['root']}")
    lines.append(f"Directories scanned: {summary['directories_scanned']}")
    lines.append(f"Files scanned: {report['scanned_files']}")
    lines.append(
        "Third-party items: "
        f"{summary['third_party_items']} | Extensions/Add-ons: {summary['extensions_and_addons']} | "
        f"Findings H/M/L: {summary['high_findings']}/{summary['medium_findings']}/{summary['low_findings']}"
    )
    lines.append("")

    lines.append("Directories Scanned")
    for directory in report["scanned_directories"]:
        lines.append(f"- {directory}")
    lines.append("")

    lines.append("Findings by Severity")
    if report["findings"]:
        for severity in ("high", "medium", "low"):
            matches = [finding for finding in report["findings"] if finding["severity"] == severity]
            if matches:
                lines.append(f"- {severity.upper()} ({len(matches)})")
                for finding in matches:
                    location = finding["file"]
                    if finding.get("line"):
                        location += f":{finding['line']}"
                    lines.append(f"  - {finding['title']} at {location}")
    else:
        lines.append("- No suspicious patterns were detected by the local heuristics.")
    lines.append("")

    lines.append("Flagged Files")
    severity_order = {"high": 0, "medium": 1, "low": 2}
    if flagged_files:
        for file_result in flagged_files:
            top = sorted(file_result["findings"], key=lambda item: severity_order.get(item["severity"], 9))[0]
            status = f"{len(file_result['findings'])} finding(s), highest={top['severity']}"
            lines.append(f"- {file_result['path']} [{status}]")
            for finding in file_result["findings"]:
                location = f"line {finding['line']}" if finding.get("line") else "file-level"
                lines.append(f"  - {finding['severity'].upper()} {finding['title']} ({location})")
                lines.append(f"    evidence: {finding['evidence']}")
                lines.append(f"    recommendation: {finding['recommendation']}")
    else:
        lines.append("- No flagged files.")
    lines.append("")

    lines.append("Clean Files")
    if clean_files:
        for file_result in clean_files:
            lines.append(f"- {file_result['path']} [OK]")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("Files Scanned")
    for file_result in report["file_results"]:
        status = "OK"
        if file_result["findings"]:
            top = sorted(file_result["findings"], key=lambda item: severity_order.get(item["severity"], 9))[0]
            status = f"{len(file_result['findings'])} finding(s), highest={top['severity']}"
        lines.append(f"- {file_result['path']} [{status}]")
    lines.append("")

    lines.append("Third-Party Inventory")
    if report["inventory"]:
        for item in report["inventory"]:
            lines.append(
                f"- [{item['category']}] {item['name']} ({item['ecosystem']}) "
                f"version={item['version']} source={item['source_file']}"
            )
            for note in item.get("notes", []):
                lines.append(f"  note: {note}")
    else:
        lines.append("- No supported dependency manifests or extension descriptors were found.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory third-party components and flag suspicious security patterns.")
    parser.add_argument("path", nargs="?", default=".", help="Repository or project path to scan.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Path not found: {root}", file=sys.stderr)
        return 1

    report = scan(root)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
