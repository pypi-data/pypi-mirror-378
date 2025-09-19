from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from packaging.version import InvalidVersion, Version

from rtx.utils import detect_files, read_json, read_toml, read_yaml


def normalize_version(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return "0.0.0"
    try:
        return str(Version(raw))
    except InvalidVersion:
        return raw


def load_json_dependencies(path: Path, key: str = "dependencies") -> Dict[str, str]:
    data = read_json(path)
    section = data.get(key, {}) if isinstance(data, dict) else {}
    return {name: str(spec) for name, spec in section.items()}


def load_lock_dependencies(path: Path) -> Dict[str, str]:
    data = read_json(path)
    if isinstance(data, dict) and "packages" in data:
        return {
            _normalize_lock_name(name): str(meta.get("version", "0.0.0"))
            for name, meta in data["packages"].items()
            if isinstance(meta, dict)
        }
    if isinstance(data, dict) and "dependencies" in data:
        out: Dict[str, str] = {}
        for name, info in data["dependencies"].items():
            if isinstance(info, dict) and "version" in info:
                out[_normalize_lock_name(name)] = str(info["version"])
        return out
    return {}


def _normalize_lock_name(name: str) -> str:
    if name.startswith('./'):
        name = name[2:]
    if name.startswith('node_modules/'):
        name = name.split('/', 1)[1]
    return name


def read_poetry_lock(path: Path) -> Dict[str, str]:
    content = read_toml(path)
    out: Dict[str, str] = {}
    for package in content.get("package", []):
        if isinstance(package, dict):
            name = package.get("name")
            version = package.get("version")
            if isinstance(name, str) and isinstance(version, str):
                out[name] = version
    return out


def read_uv_lock(path: Path) -> Dict[str, str]:
    data = read_json(path)
    out: Dict[str, str] = {}
    for entry in data.get("projects", []):
        if isinstance(entry, dict):
            deps = entry.get("dependencies", [])
            for dep in deps:
                if isinstance(dep, dict):
                    name = dep.get("name")
                    version = dep.get("version")
                    if isinstance(name, str) and isinstance(version, str):
                        out[name] = version
    return out


def read_requirements(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "==" in line:
            name, version = line.split("==", 1)
            out[name.strip()] = version.strip()
        else:
            out[line] = "*"
    return out


def read_gemfile_lock(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith(" ") or line.startswith("-"):
            continue
        if " (" in line and ")" in line:
            name, version = line.split(" (", 1)
            out[name.strip()] = version.rstrip(")")
    return out


def read_maven_pom(path: Path) -> Dict[str, str]:
    import xml.etree.ElementTree as ET

    tree = ET.parse(path)
    root = tree.getroot()
    namespace = "" if not root.tag.startswith("{") else root.tag.split("}", 1)[0] + "}"
    deps: Dict[str, str] = {}
    for dependency in root.findall(f".//{namespace}dependency"):
        group = dependency.findtext(f"{namespace}groupId") or ""
        artifact = dependency.findtext(f"{namespace}artifactId") or ""
        version = dependency.findtext(f"{namespace}version") or "0.0.0"
        if group and artifact:
            deps[f"{group}:{artifact}"] = version
    return deps


def read_go_mod(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    in_block = False
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith(("module", "//", "replace")):
            continue
        if line.startswith("require ("):
            in_block = True
            continue
        if in_block and line.startswith(")"):
            in_block = False
            continue
        if line.startswith("require") and not line.endswith("("):
            parts = line.split()
            if len(parts) >= 3:
                _, module, version = parts[:3]
                out[module] = version
            continue
        if in_block and " " in line:
            module, version = line.split()[:2]
            out[module] = version
        elif " " in line:
            module, version = line.split()[:2]
            out[module] = version
    return out


def read_cargo_lock(path: Path) -> Dict[str, str]:
    content = read_toml(path)
    out: Dict[str, str] = {}
    for package in content.get("package", []):
        if isinstance(package, dict):
            name = package.get("name")
            version = package.get("version")
            if isinstance(name, str) and isinstance(version, str):
                out[name] = version
    return out


def read_composer_lock(path: Path) -> Dict[str, str]:
    data = read_json(path)
    out: Dict[str, str] = {}
    for section in ("packages", "packages-dev"):
        for package in data.get(section, []):
            if isinstance(package, dict):
                name = package.get("name")
                version = package.get("version")
                if isinstance(name, str) and isinstance(version, str):
                    out[name] = version
    return out


def read_environment_yml(path: Path) -> Dict[str, str]:
    data = read_yaml(path) or {}
    deps = data.get("dependencies", [])
    out: Dict[str, str] = {}
    for entry in deps:
        if isinstance(entry, str) and "=" in entry:
            name, version = entry.split("=", 1)
            out[name] = version
        elif isinstance(entry, dict) and "pip" in entry:
            for package in entry["pip"]:
                if "==" in package:
                    name, version = package.split("==", 1)
                    out[name] = version
                else:
                    out[package] = "*"
    return out


def read_brewfile(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("brew"):
            parts = line.split(",")
            name = parts[0].split()[1].strip("'\"")
            version = "latest"
            if len(parts) > 1 and "version" in parts[1]:
                version = parts[1].split(":")[1].strip(" \"'")
            out[name] = version
    return out


def read_packages_lock(path: Path) -> Dict[str, str]:
    data = read_json(path)
    out: Dict[str, str] = {}
    dependencies = data.get("dependencies", {})
    if isinstance(dependencies, dict):
        for name, info in dependencies.items():
            if isinstance(info, dict) and "resolved" in info:
                version = info.get("resolved", "0.0.0")
            else:
                version = info.get("version", "0.0.0") if isinstance(info, dict) else "0.0.0"
            out[name] = version
    return out


def read_dockerfile(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("RUN"):
            for segment in line.split("&&"):
                segment = segment.strip()
                if "pip install" in segment:
                    packages = segment.split("pip install", 1)[1].strip().split()
                    for package in packages:
                        if "==" in package:
                            name, version = package.split("==", 1)
                            out[f"pypi:{name}"] = version
                if "npm install" in segment:
                    packages = segment.split("npm install", 1)[1].strip().split()
                    for package in packages:
                        if "@" in package:
                            name, version = package.split("@", 1)
                            out[f"npm:{name}"] = version
    return out
