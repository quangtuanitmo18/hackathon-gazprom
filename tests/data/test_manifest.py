from hashlib import sha256
import pytest
from productpulse.data.manifest import build_provenance_manifest


def test_manifest_records_provenance_and_checksum(tmp_path):
    f = tmp_path / "sample.csv"
    f.write_bytes(b"ticket_id,text\n1,hello\n")
    m = build_provenance_manifest("https://example.org/dataset", "CC-BY-4.0", f)
    assert m["sha256"] == sha256(f.read_bytes()).hexdigest()
    assert m["source_url"] == "https://example.org/dataset"
    assert m["license_id"] == "CC-BY-4.0"
    assert m["size_bytes"] == len(f.read_bytes())


def test_manifest_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        build_provenance_manifest("https://example.org", "CC-BY-4.0", tmp_path/"missing.csv")
