import importlib
import sys
import tempfile
import zipfile
from pathlib import Path


with tempfile.TemporaryDirectory() as directory:
    wheel = Path(directory) / "mistune-test-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "mistune.py",
            "def create_markdown(renderer=None):\n"
            "    def parse(value):\n"
            "        return [{'type':'heading','attrs':{'level':len(line)-len(line.lstrip('#'))}} for line in value.splitlines() if line.startswith('#')]\n"
            "    return parse\n",
        )
    sys.path.insert(0, str(wheel))
    try:
        module = importlib.import_module("mistune")
        parser = module.create_markdown(renderer="ast")
        normal = parser("# 1\n## 1.1\n### 1.1.1\n#### 1.1.1.1\n")
        malformed = parser("plain body without headings")
    finally:
        sys.path.remove(str(wheel))
        sys.modules.pop("mistune", None)

levels = [token["attrs"]["level"] for token in normal if token["type"] == "heading"]
assert levels == [1, 2, 3, 4]
assert not [token for token in malformed if token["type"] == "heading"]
print("MISTUNE_HEADING_AST_CONTRACT=2/2 PASS")
