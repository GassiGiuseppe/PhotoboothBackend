# app/storage/local.py
import os
import uuid
from pathlib import Path
from typing import Optional
import shutil
import base64

class StorageError(Exception):
    pass


class LocalStorage:
    """
    Local mock storage that behaves like GCS:
      - stores files as <uuid>.png under base_dir
      - returns mock "signed URLs" served by /photos/raw/{id}
    """
    def __init__(self, base_dir: str = "/data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # --- save ---

    def save_base64(self, b64: str) -> str:
        # here the uuid is generated
        raw = base64.b64decode(b64, validate=True)
        # optional: PNG magic check (comment out if you don't want it)
        if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
            raise StorageError("only PNG is allowed")
        pid = str(uuid.uuid4())
        (self.base_dir / f"{pid}.png").write_bytes(raw)
        return pid

    # --- signed url + raw access ---


    def signed_url(self, photo_id: str) -> str:
        # ... it doesnt work correclty
        return f"/photos/raw/{photo_id}"

    def open_bytes(self, photo_id: str) -> bytes:
        p = self.base_dir / f"{photo_id}.png"
        if not p.exists():
            raise StorageError("not found")
        return p.read_bytes()

    # --- delete ---

    def delete(self, photo_id: str) -> bool:
        p = self.base_dir / f"{photo_id}.png"
        if p.exists():
            p.unlink()
            return True
        return False


def get_storage_backend():
    backend = os.getenv("STORAGE_BACKEND", "local").lower()
    if backend == "local":
        return LocalStorage(os.getenv("LOCAL_DATA_DIR", "/data"))
    raise StorageError(f"Unsupported backend: {backend}")
