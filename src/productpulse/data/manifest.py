"""Immutable identity and attribution for locally approved dataset files."""
from hashlib import sha256
from pathlib import Path


def build_provenance_manifest(source_url: str, license_id: str, file_path: Path) -> dict:
    raw = Path(file_path).read_bytes()
    return {"source_url": source_url, "license_id": license_id,
            "sha256": sha256(raw).hexdigest(), "size_bytes": len(raw),
            "file_name": Path(file_path).name}
