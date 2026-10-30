import hashlib

import pytest

from productpulse.data.manifest import build_provenance_manifest


def test_manifest_computes_content_sha256_without_exposing_contents(tmp_path):
    sample = tmp_path / "example.csv"
    data = b"id,text\n1,example\n"
    sample.write_bytes(data)
    manifest = build_provenance_manifest("https://zenodo.org/records/7648117", "CC-BY-4.0", sample)
    assert manifest == {
        "source_url": "https://zenodo.org/records/7648117",
        "license_id": "CC-BY-4.0",
        "file_name": "example.csv",
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    assert "1,example" not in str(manifest)


def test_manifest_rejects_unknown_license(tmp_path):
    sample = tmp_path / "fixture.csv"
    sample.write_text("x")
    with pytest.raises(ValueError, match="license"):
        build_provenance_manifest("https://example.org/data", "", sample)


def test_manifest_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        build_provenance_manifest("https://example.org/data", "CC-BY-4.0", tmp_path / "missing.csv")


def test_manifest_rejects_url_bearing_credentials(tmp_path):
    sample = tmp_path / "fixture.csv"
    sample.write_text("x")
    with pytest.raises(ValueError, match="credentials|query"):
        build_provenance_manifest("https://user:secret@example.org/data?token=secret", "CC-BY-4.0", sample)
