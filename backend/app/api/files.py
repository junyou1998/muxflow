import os
import re
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from ..config import STORAGE_DIR

router = APIRouter(prefix="/api/files", tags=["files"])

def natural_sort_key(s: str):
    """Sort strings containing numbers naturally (e.g. Ep 2 before Ep 10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)]

class ListFilesRequest(BaseModel):
    directory: str
    extensions: Optional[List[str]] = None

@router.get("/browse")
def browse_directory(path: Optional[str] = Query(None)):
    """Browse server-side filesystem for the file picker modal."""
    target_path = path or STORAGE_DIR
    target_path = os.path.abspath(target_path)

    if not os.path.exists(target_path) or not os.path.isdir(target_path):
        target_path = STORAGE_DIR
        if not os.path.exists(target_path):
            target_path = "/"

    try:
        entries = os.scandir(target_path)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied to access directory")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    directories = []
    files = []

    for entry in entries:
        try:
            if entry.name.startswith("."):
                continue
            if entry.is_dir(follow_symlinks=True):
                directories.append({
                    "name": entry.name,
                    "path": entry.path,
                    "is_dir": True,
                })
            elif entry.is_file(follow_symlinks=True):
                ext = entry.name.split(".")[-1].lower() if "." in entry.name else ""
                files.append({
                    "name": entry.name,
                    "path": entry.path,
                    "is_dir": False,
                    "size": entry.stat().st_size,
                    "extension": ext
                })
        except (PermissionError, FileNotFoundError):
            continue

    directories.sort(key=lambda x: natural_sort_key(x["name"]))
    files.sort(key=lambda x: natural_sort_key(x["name"]))

    parent_path = os.path.dirname(target_path) if target_path != "/" else None

    # Quick shortcut roots
    quick_roots = [
        {"name": "Storage (/storage)", "path": STORAGE_DIR},
        {"name": "Root (/)", "path": "/"},
        {"name": "Home", "path": str(Path.home())}
    ]

    return {
        "current_path": target_path,
        "parent_path": parent_path,
        "quick_roots": quick_roots,
        "directories": directories,
        "files": files,
    }

@router.post("/list_files")
def list_directory_files(req: ListFilesRequest):
    """List and filter files in a given directory by extensions with natural sorting."""
    target_dir = os.path.abspath(req.directory)
    if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
        raise HTTPException(status_code=404, detail="Directory not found")

    ext_set = {e.lower().lstrip(".") for e in req.extensions} if req.extensions else None
    matched_files = []

    try:
        with os.scandir(target_dir) as entries:
            for entry in entries:
                if entry.is_file(follow_symlinks=True):
                    ext = entry.name.split(".")[-1].lower() if "." in entry.name else ""
                    if ext_set is None or ext in ext_set:
                        matched_files.append({
                            "name": entry.name,
                            "path": entry.path,
                            "size": entry.stat().st_size,
                            "extension": ext
                        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    matched_files.sort(key=lambda x: natural_sort_key(x["name"]))
    return {"directory": target_dir, "files": matched_files}
