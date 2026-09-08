"""doit task graph for the local, free TOOL044 factory."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PY = sys.executable

def task_function_state():
    return {"actions": [[PY, "-X", "utf8", str(HERE / "tool044_function_state.py")]],
            "file_dep": [str(HERE / "unified_open_ledger.json"), str(HERE / "VERIFIED_COMPONENT_REGISTRY.json")],
            "targets": [str(HERE / "tool044_function_state.json")]}

def task_external_harvest():
    return {"actions": [[PY, "-X", "utf8", str(HERE / "tool044_atomic_watch.py"), "--external", "--trigger-source", "SCHEDULED"]],
            "task_dep": ["function_state"], "verbosity": 2}

def task_observer_projection():
    return {"actions": [[PY, "-X", "utf8", str(HERE.parent / "tool043" / "night_observer.py")]],
            "task_dep": ["external_harvest"], "verbosity": 2}
