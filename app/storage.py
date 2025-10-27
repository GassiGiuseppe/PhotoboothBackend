import os
import uuid
from pathlib import Path
import shutil

# Custom exception type for storage errors
class StorageError(Exception):
    pass

class LocalStorage:
    """
    Mock storage backend that saves files to a local folder.
    In production, replace with a GCSStorage class.
    """
    def __init__(self, base_dir: str = "/data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, upload_file):
        try:
            file_id = str(uuid.uuid4())
            filename = upload_file.filename
            dest_path = self.base_dir / f"{file_id}_{filename}"

            # Save uploaded file to disk
            with open(dest_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)

            return {
                "id": file_id,
                "filename": filename,
                "backend": "local",
                "url": f"/mock/{file_id}/{filename}",  # mock URL placeholder
            }

        except Exception as e:
            raise StorageError(f"Failed to save file: {e}")

def get_storage_backend():
    """
    Choose which storage backend to use.
    For now, always return LocalStorage().
    Later, you can decide based on an env variable.
    """
    backend = os.getenv("STORAGE_BACKEND", "local").lower()
    if backend == "local":
        return LocalStorage()
    else:
        raise StorageError(f"Unsupported backend: {backend}")
