import os
from uuid import UUID
from typing import List

from fastapi import APIRouter, HTTPException, Response
from starlette import status

from app.models.models import PhotoUpload, PhotoItem, PhotoSingle
from app.storage.storage import LocalStorage, StorageError
from app.storage.local_ids_db.adapter import PhotoIndexAsync


class Service():

    def __init__(self) -> None:
        DATABASE_URL = os.environ["DATABASE_URL"]
        self._local_db_index = PhotoIndexAsync(DATABASE_URL)
        self._store = LocalStorage(os.getenv("LOCAL_DATA_DIR", "/data"))



    async def create_photo(self, payload: PhotoUpload):
        """
        upload nuova foto
        body: {"data": "<base64 PNG>"}
        returns: {"id": uuid}
        """
        try:
            pid = self._store.save_base64(payload.data)
            # we don't receive a filename in this API; store a placeholder
            await self._local_db_index.add(pid, "unknown.png")
            return {"id": UUID(pid)}
        except StorageError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="internal error")


    async def list_photos(self, page: int = 1, limit: int = 10):
        """
        restituisce lista foto paginata
        """
        ids = await self._local_db_index.retrieve(limit, page)
        return [{"id": UUID(pid), "url": self._store.signed_url(pid)} for pid in ids]


    async def get_photo(self, photo_id: UUID):
        """
        restituisce la foto corrispondente allo uuid fornito (as signed URL)
        """
        # no DB check required for mock; signed_url is deterministic
        # if you want stricter behavior, you can check presence on disk
        return {"id": photo_id, "url": self._store.signed_url(str(photo_id))}


    async def delete_photo(self, photo_id: UUID):
        """
        elimina la foto corrispondente allo uuid fornito
        """
        # photo id
        pid = str(photo_id)
        # delete from disk first; if missing, report 404
        removed = self._store.delete(pid)
        if not removed:
            raise HTTPException(status_code=404, detail="not found")
        # best-effort DB delete (idempotent)
        await self._local_db_index.delete(pid)
        return {"message": "OK"}



    async def delete_latest(self):
        """
        elimina l’ultima foto caricata
        """
        pid = await self._local_db_index.latest()
        if not pid:
            raise HTTPException(status_code=404, detail="no photos")
        removed = self._store.delete(pid)
        if not removed:
            # file missing but index has a reference → clean index anyway
            await self._local_db_index.delete(pid)
            raise HTTPException(status_code=404, detail="not found")
        await self._local_db_index.delete(pid)
        return {"message": "OK"}


    # Convenience endpoint so your mock signed_url works:
    async def get_photo_raw(self, photo_id: UUID):
        try:
            data = self._store.open_bytes(str(photo_id))
        except StorageError:
            raise HTTPException(status_code=404, detail="not found")
        return Response(content=data, media_type="image/png")
