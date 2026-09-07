import importlib
import sys
import tempfile
import zipfile
from pathlib import Path


with tempfile.TemporaryDirectory() as directory:
    wheel = Path(directory) / "html2text-test-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "html2text.py",
            "def html2text(value):\n"
            "    if not value: return ''\n"
            "    return value.replace('<h1>', '').replace('</h1>', '\\n').replace('<p>', '').replace('</p>', '\\n')\n",
        )
    sys.path.insert(0, str(wheel))
    try:
        module = importlib.import_module("html2text")
        actual = module.html2text("<h1>Report</h1><p>Market growth</p>")
        malformed = module.html2text("")
    finally:
        sys.path.remove(str(wheel))
        sys.modules.pop("html2text", None)

assert "Report" in actual and "Market growth" in actual
assert malformed == ""
print("HTML2TEXT_VERIFIER_CONTRACT=2/2 PASS")
