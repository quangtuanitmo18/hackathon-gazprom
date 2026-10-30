"""Content-addressed provenance for an approved local data artifact."""

from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit


def build_provenance_manifest(source_url: str, license_id: str, file_path: Path) -> dict:
    """Hash local bytes without recording any ticket content or local path.

    This does not confer rights to redistribute the file; verify license and
    origin independently. A manifest describes evidence, not a guarantee.
    """
    if not license_id or not license_id.strip():
        raise ValueError("license_id is required")
    parsed = urlsplit(source_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("source_url must be an absolute http(s) URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("source_url must not contain credentials, query parameters or fragments")
    path = Path(file_path)
    digest = sha256()
    byte_count = 0
    with path.open("rb") as file:
        while data := file.read(1024 * 1024):
            digest.update(data)
            byte_count += len(data)
    return {
        "source_url": source_url,
        "license_id": license_id.strip(),
        "file_name": path.name,
        "size_bytes": byte_count,
        "sha256": digest.hexdigest(),
    }
