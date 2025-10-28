import os
from uuid import UUID
from typing import List

from fastapi import APIRouter, HTTPException, Response
from starlette import status

from app.models.models import PhotoUpload, PhotoItem, PhotoSingle
from app.storage.storage import LocalStorage, StorageError
from app.storage.local_ids_db.adapter import PhotoIndexAsync

router = APIRouter(prefix="/photos", tags=["photos"])

# deps
DATABASE_URL = os.environ["DATABASE_URL"]
index = PhotoIndexAsync(DATABASE_URL)
store = LocalStorage(os.getenv("LOCAL_DATA_DIR", "/data"))

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_photo(payload: PhotoUpload):
    """
    upload nuova foto
    body: {"data": "<base64 PNG>"}
    returns: {"id": uuid}
    """
    try:
        pid = store.save_base64(payload.data)
        # we don't receive a filename in this API; store a placeholder
        await index.add(pid, "unknown.png")
        return {"id": UUID(pid)}
    except StorageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="internal error")

@router.get("", response_model=List[PhotoItem])
async def list_photos(page: int = 1, limit: int = 10):
    """
    restituisce lista foto paginata
    """
    ids = await index.retrieve(limit, page)
    return [{"id": UUID(pid), "url": store.signed_url(pid)} for pid in ids]

@router.get("/{photo_id}", response_model=PhotoSingle)
async def get_photo(photo_id: UUID):
    """
    restituisce la foto corrispondente allo uuid fornito (as signed URL)
    """
    # no DB check required for mock; signed_url is deterministic
    # if you want stricter behavior, you can check presence on disk
    return {"id": photo_id, "url": store.signed_url(str(photo_id))}

@router.delete("/{photo_id}")
async def delete_photo(photo_id: UUID):
    """
    elimina la foto corrispondente allo uuid fornito
    """
    pid = str(photo_id)
    # delete from disk first; if missing, report 404
    removed = store.delete(pid)
    if not removed:
        raise HTTPException(status_code=404, detail="not found")
    # best-effort DB delete (idempotent)
    await index.delete(pid)
    return {"message": "OK"}


@router.delete("/latest")
async def delete_latest():
    """
    elimina l’ultima foto caricata
    """
    pid = await index.latest()
    if not pid:
        raise HTTPException(status_code=404, detail="no photos")
    removed = store.delete(pid)
    if not removed:
        # file missing but index has a reference → clean index anyway
        await index.delete(pid)
        raise HTTPException(status_code=404, detail="not found")
    await index.delete(pid)
    return {"message": "OK"}


# Convenience endpoint so your mock signed_url works:
@router.get("/raw/{photo_id}")
async def get_photo_raw(photo_id: UUID):
    try:
        data = store.open_bytes(str(photo_id))
    except StorageError:
        raise HTTPException(status_code=404, detail="not found")
    return Response(content=data, media_type="image/png")
