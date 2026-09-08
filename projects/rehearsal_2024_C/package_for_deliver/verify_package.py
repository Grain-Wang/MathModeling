"""Verify the integrity of the figure handoff package using only stdlib."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> int:
    manifest = json.loads((ROOT / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
    failures = []
    for item in manifest["files"]:
        path = ROOT / item["package_path"]
        actual = sha256(path) if path.is_file() else None
        if actual != item["sha256"]:
            failures.append({"path": item["package_path"], "expected": item["sha256"], "actual": actual})
    if failures:
        print(json.dumps({"status": "FAIL", "failures": failures}, ensure_ascii=False, indent=2))
        return 1
    print(f"PACKAGE_VERIFY_PASS: {len(manifest['files'])} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
