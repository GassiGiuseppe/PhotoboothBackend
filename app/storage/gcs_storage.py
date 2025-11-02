from __future__ import annotations
import base64, io, os
from uuid import uuid4
from datetime import timedelta
from typing import Optional

from google.cloud import storage

class GCSStorage:
    def __init__(self, bucket: str, prefix: str = "", default_content_type: str = "image/png"):
        self.client = storage.Client()  # uses GOOGLE_APPLICATION_CREDENTIALS
        self.bucket = self.client.bucket(bucket)
        self.prefix = prefix.strip("/")
        self.default_content_type = default_content_type
        # TTL for signed URLs (seconds)
        self._sign_ttl = int(os.getenv("GCS_SIGN_URL_TTL", "3600"))

    def _key(self, pid: str) -> str:
        return f"{self.prefix}/{pid}" if self.prefix else pid

    # ---- API expected by your Service ----
    def save_base64(self, b64: str) -> str:
        raw = base64.b64decode(b64)
        return self.save_bytes(raw)

    def save_bytes(self, data: bytes) -> str:
        pid = str(uuid4())
        blob = self.bucket.blob(self._key(pid))
        # Set content_type so browsers know it’s an image
        blob.upload_from_file(io.BytesIO(data), size=len(data), content_type=self.default_content_type)
        return pid

    def open_bytes(self, pid: str) -> bytes:
        blob = self.bucket.blob(self._key(pid))
        if not blob.exists():
            raise FileNotFoundError(pid)
        return blob.download_as_bytes()

    def delete(self, pid: str) -> bool:
        blob = self.bucket.blob(self._key(pid))
        try:
            blob.delete()  # idempotent: 404 if missing
            return True
        except Exception:
            # If you want to return False only when missing:
            # from google.api_core.exceptions import NotFound
            # if isinstance(e, NotFound): return False
            return False

    def signed_url(self, pid: str) -> str:
        blob = self.bucket.blob(self._key(pid))
        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=self._sign_ttl),
            method="GET",
        )
