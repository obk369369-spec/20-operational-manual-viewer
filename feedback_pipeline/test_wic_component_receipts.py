from __future__ import annotations

import base64, gzip, hashlib, io, json, tarfile, tempfile
from pathlib import Path

from wic_component_receipts import assemble, orchestrate, verify_component


def make_tgz(member: str, data: bytes) -> bytes:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w:") as tar:
        info = tarfile.TarInfo(member)
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    return gzip.compress(raw.getvalue())


with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    wheel = root / "component.whl"
    wheel.write_bytes(b"verified-wheel")
    js = root / "compat.js"
    js.write_bytes(b"verified-js")
    archive = make_tgz("package/dist/compat.js", js.read_bytes())
    pypi = json.dumps({"info": {"name": "component", "version": "1.0", "author": "owner", "license": "BSD"}, "urls": [{"filename": wheel.name, "size": wheel.stat().st_size, "yanked": False, "digests": {"sha256": hashlib.sha256(wheel.read_bytes()).hexdigest()}}], "vulnerabilities": []}).encode()
    npm = json.dumps({"name": "idb-keyval", "version": "6.2.2", "license": "Apache-2.0", "maintainers": [{"name": "owner"}], "dependencies": {}, "dist": {"tarball": "https://fixture/archive.tgz", "integrity": "sha512-" + base64.b64encode(hashlib.sha512(archive).digest()).decode(), "shasum": hashlib.sha1(archive).hexdigest()}}).encode()
    blobs = {"https://fixture/pypi": pypi, "https://fixture/npm": npm, "https://fixture/archive.tgz": archive}
    fetch = blobs.__getitem__
    common = {"source": "fixture", "tag": "v1", "commit": "a" * 40, "acquired_at": "fixture", "canonical_path": "fixture", "dependencies": []}
    py = {**common, "component_id": "PY", "ecosystem": "pypi", "version": "1.0", "license": "BSD", "local_path": str(wheel), "metadata_url": "https://fixture/pypi", "release_filename": wheel.name}
    node = {**common, "component_id": "NODE", "ecosystem": "npm", "version": "6.2.2", "license": "Apache-2.0", "local_path": str(js), "metadata_url": "https://fixture/npm", "release_members": ["package/dist/compat.js"]}
    no_ready = {"component_id": "MISSING", "availability": "NO_READY_COMPONENT", "reason": "no unmodified commercial-ready release"}
    assert verify_component(py, fetch)["status"] == "COMPONENT_VERIFIED"
    assert verify_component(node, fetch)["status"] == "COMPONENT_VERIFIED"
    js.write_bytes(b"tampered")
    assert verify_component(node, fetch)["status"] == "RECEIPT_MISMATCH"
    js.write_bytes(b"verified-js")
    result = orchestrate({"components": [py, node, no_ready]}, fetch)
    assert result["status"] == "PASS"
    assert result["assembly"]["component_verified"] == 2
    assert result["assembly"]["no_ready_component"] == ["MISSING"]
    assert assemble([{"component_id": "X", "status": "SHELL_OR_INVALID"}])["status"] == "ASSEMBLY_PARTIAL"
    print("6/6 PASS")
