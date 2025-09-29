from pathlib import Path
from typing import List

# Directory inside the repo where you will drop files
DATA_FILES_DIR = Path("data_files")

# Allowed extensions we auto-scan
ALLOWED_EXTS = {".csv", ".json", ".txt", ".md"}

def list_data_files() -> List[str]:
    """
    Recursively scan data_files/ for allowed extensions and return relative paths (str).
    """
    if not DATA_FILES_DIR.exists():
        return []
    files: List[str] = []
    for p in DATA_FILES_DIR.rglob("*"):
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTS:
            files.append(str(p))
    return files

# Backward-compat alias used elsewhere
DEFAULT_LOCAL_FILES: List[str] = list_data_files()
