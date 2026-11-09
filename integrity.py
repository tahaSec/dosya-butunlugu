#!/usr/bin/env python3
"""Create and verify a SHA-256 manifest for files in a chosen directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules"}
CHUNK_SIZE = 1024 * 1024


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def walk_files(root: Path, ignored: set[Path] | None = None):
    ignored = ignored or set()
    for candidate in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in candidate.relative_to(root).parts):
            continue
        if candidate.is_symlink() or not candidate.is_file():
            continue
        if candidate.resolve() in ignored:
            continue
        yield candidate


def create_manifest(root: Path, output: Path) -> int:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Klasör bulunamadı: {root}")
    ignored = {output.resolve()} if output.exists() else set()
    files = {}
    for path in walk_files(root, ignored):
        files[path.relative_to(root).as_posix()] = {
            "sha256": digest_file(path), "size": path.stat().st_size
        }
    document = {
        "format": "sha256-manifest-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root_name": root.name,
        "files": files,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Manifest yazıldı: {output}")
    print(f"Özetlenen dosya: {len(files)}")
    return 0


def verify_manifest(root: Path, manifest_path: Path) -> int:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Klasör bulunamadı: {root}")
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    if document.get("format") != "sha256-manifest-v1" or not isinstance(document.get("files"), dict):
        raise ValueError("Manifest biçimi tanınmıyor.")

    baseline = document["files"]
    current = {path.relative_to(root).as_posix(): path for path in walk_files(root, {manifest_path.resolve()})}
    missing = sorted(set(baseline) - set(current))
    added = sorted(set(current) - set(baseline))
    changed = []
    for relative in sorted(set(baseline) & set(current)):
        actual = digest_file(current[relative])
        if actual != baseline[relative].get("sha256"):
            changed.append(relative)

    print(f"Manifest: {manifest_path}")
    print(f"Beklenen: {len(baseline)} dosya  |  Şimdiki: {len(current)} dosya")
    for label, items in (("DEĞİŞMİŞ", changed), ("EKSİK", missing), ("YENİ", added)):
        print(f"\n{label} ({len(items)})")
        print("\n".join(f"- {item}" for item in items) if items else "- Yok")
    if not (missing or added or changed):
        print("\nBütün dosyalar manifest ile eşleşiyor.")
        return 0
    return 1


def main() -> int:
    configure_console()
    parser = argparse.ArgumentParser(description="Seçtiğin klasörde dosya değişikliklerini SHA-256 ile izle.")
    commands = parser.add_subparsers(dest="command", required=True)
    baseline = commands.add_parser("baseline", help="Başlangıç manifesti oluştur")
    baseline.add_argument("folder", type=Path, help="İzlenecek klasör")
    baseline.add_argument("--output", type=Path, default=Path("integrity-manifest.json"), help="Manifest dosyası")
    check = commands.add_parser("check", help="Manifest ile klasörü karşılaştır")
    check.add_argument("folder", type=Path, help="İzlenen klasör")
    check.add_argument("manifest", type=Path, help="Önceden oluşturulmuş manifest")
    args = parser.parse_args()
    try:
        if args.command == "baseline":
            return create_manifest(args.folder, args.output)
        if not args.manifest.is_file():
            raise ValueError(f"Manifest bulunamadı: {args.manifest}")
        return verify_manifest(args.folder, args.manifest)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Hata: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
