from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from rtx.api import scan_project
from rtx.advisory import AdvisoryClient
from rtx.exceptions import ManifestNotFound, ReportRenderingError, RTXError
from rtx.models import Advisory, Dependency, PackageFinding, Report, Severity, TrustSignal
from rtx.policy import TrustPolicyEngine
from rtx.registry import SCANNER_CLASSES
from rtx.reporting import render, render_json, render_table
from rtx.sbom import write_sbom

console = Console()


def _configure_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="[%(levelname)s] %(message)s")


def cmd_scan(args: argparse.Namespace) -> int:
    _configure_logging(args.log_level)
    managers = args.manager or None
    fmt = args.format.lower()
    if fmt not in {"table", "json", "html"}:
        console.print(f"[red]Unsupported format '{args.format}'. Choose table, json, or html.[/red]")
        return 2
    try:
        report = scan_project(Path(args.path), managers)
    except ManifestNotFound as exc:
        console.print(f"[red]{exc}[/red]")
        return 3

    try:
        if fmt == "table":
            render_table(report, console=console)
        else:
            if not args.output:
                console.print("[red]--output is required for json/html rendering[/red]")
                return 2
            render(report, fmt=fmt, output=Path(args.output))
    except ReportRenderingError as exc:
        console.print(f"[red]Failed to render report:[/] {exc}")
        return 2

    if args.json_output:
        render_json(report, path=Path(args.json_output))
    if args.html_output:
        render(report, fmt="html", output=Path(args.html_output))
    if args.sbom_output:
        write_sbom(report, path=str(args.sbom_output))

    return report.exit_code()


def cmd_pre_upgrade(args: argparse.Namespace) -> int:
    _configure_logging(args.log_level)
    report = scan_project(Path(args.path), [args.manager] if args.manager else None)
    baseline = next(
        (
            finding
            for finding in report.findings
            if finding.dependency.name == args.package
            and (not args.manager or finding.dependency.ecosystem == args.manager)
        ),
        None,
    )
    if baseline is None:
        console.print(f"[yellow]Package '{args.package}' not found in current dependency graph[/yellow]")
        return 1

    dependency = Dependency(
        ecosystem=baseline.dependency.ecosystem,
        name=args.package,
        version=args.version,
        direct=baseline.dependency.direct,
        manifest=baseline.dependency.manifest,
        metadata=baseline.dependency.metadata,
    )

    async def evaluate() -> PackageFinding:
        async with AdvisoryClient() as advisory_client:
            advisory_map = await advisory_client.fetch_advisories([dependency])
        engine = TrustPolicyEngine()
        try:
            return await engine.analyze(dependency, advisory_map.get(dependency.coordinate, []))
        finally:
            await engine.close()

    finding = asyncio.run(evaluate())
    console.print(f"Baseline: {baseline.dependency.version} → {baseline.verdict.value}")
    console.print(f"Proposed: {args.version} → {finding.verdict.value}")

    if finding.verdict in (Severity.CRITICAL, Severity.HIGH):
        return 2
    if finding.verdict == Severity.MEDIUM:
        return 1
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    _configure_logging(args.log_level)
    fmt = args.format.lower()
    if fmt not in {"table", "json", "html"}:
        console.print(f"[red]Unsupported format '{args.format}'.[/red]")
        return 2
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid report JSON:[/] {exc}")
        return 4
    report = _report_from_payload(payload)
    if fmt == "table":
        render_table(report, console=console)
    else:
        if not args.output:
            console.print("[red]--output is required for json/html rendering[/red]")
            return 2
        render(report, fmt=fmt, output=Path(args.output))
    return report.exit_code()


def cmd_list_managers(_: argparse.Namespace) -> int:
    for name, cls in SCANNER_CLASSES.items():
        console.print(f"[bold]{name}[/bold]: {', '.join(cls.manifests)}")
    return 0


def _report_from_payload(payload: dict) -> Report:
    summary = payload.get("summary", {})
    findings_data = payload.get("findings", [])
    findings: List[PackageFinding] = []
    for entry in findings_data:
        dependency = Dependency(
            ecosystem=entry.get("ecosystem", "unknown"),
            name=entry.get("name", "unknown"),
            version=entry.get("version", "0.0.0"),
            direct=entry.get("direct", False),
            manifest=Path(entry.get("manifest", ".")),
            metadata=entry.get("metadata", {}),
        )
        advisories = [
            Advisory(
                identifier=adv.get("id", "UNKNOWN"),
                source=adv.get("source", "unknown"),
                severity=_coerce_severity(adv.get("severity", "low")),
                summary=adv.get("summary", ""),
                references=adv.get("references", []),
            )
            for adv in entry.get("advisories", [])
        ]
        signals = [
            TrustSignal(
                category=sig.get("category", "unknown"),
                severity=_coerce_severity(sig.get("severity", "low")),
                message=sig.get("message", ""),
                evidence=sig.get("evidence", {}),
            )
            for sig in entry.get("signals", [])
        ]
        score = float(entry.get("score", 0.0) or 0.0)
        findings.append(PackageFinding(dependency=dependency, advisories=advisories, signals=signals, score=score))

    generated_at = summary.get("generated_at")
    timestamp = datetime.fromisoformat(generated_at) if isinstance(generated_at, str) else datetime.utcnow()
    managers = summary.get("managers", [])
    if isinstance(managers, str):
        managers = [managers]
    return Report(
        path=Path(summary.get("path", ".")),
        managers=managers,
        findings=findings,
        generated_at=timestamp,
        stats=payload.get("stats", {}),
    )


def _coerce_severity(value: object) -> Severity:
    try:
        return Severity(str(value).lower())
    except ValueError:
        return Severity.LOW


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rtx", description="Real Tracker X dependency trust scanner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan manifests and compute trust report")
    scan_parser.add_argument("--path", default=".", help="Project root to scan")
    scan_parser.add_argument("--manager", action="append", help="Repeat for each manager to include", default=None)
    scan_parser.add_argument("--format", default="table", help="Report format: table|json|html")
    scan_parser.add_argument("--output", help="Destination for json/html output")
    scan_parser.add_argument("--json-output", help="Persist JSON report")
    scan_parser.add_argument("--html-output", help="Persist HTML report")
    scan_parser.add_argument("--sbom-output", help="Write CycloneDX SBOM")
    scan_parser.add_argument("--log-level", default="INFO", help="Logging level")
    scan_parser.set_defaults(func=cmd_scan)

    upgrade_parser = subparsers.add_parser("pre-upgrade", help="Simulate a dependency upgrade")
    upgrade_parser.add_argument("--path", default=".", help="Project root")
    upgrade_parser.add_argument("--manager", help="Package manager to target")
    upgrade_parser.add_argument("--package", required=True, help="Package name")
    upgrade_parser.add_argument("--version", required=True, help="Proposed version")
    upgrade_parser.add_argument("--log-level", default="INFO")
    upgrade_parser.set_defaults(func=cmd_pre_upgrade)

    report_parser = subparsers.add_parser("report", help="Render a stored JSON report")
    report_parser.add_argument("input", help="Path to JSON report")
    report_parser.add_argument("--format", default="table", help="table|json|html")
    report_parser.add_argument("--output", help="Destination for json/html output")
    report_parser.add_argument("--log-level", default="INFO")
    report_parser.set_defaults(func=cmd_report)

    list_parser = subparsers.add_parser("list-managers", help="List supported package managers")
    list_parser.set_defaults(func=cmd_list_managers)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
