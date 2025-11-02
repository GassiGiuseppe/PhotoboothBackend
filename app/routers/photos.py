# app/routers/photos.py

from uuid import UUID
from typing import List

from fastapi import APIRouter, Response, Query
from starlette import status

from app.models.models import PhotoUpload, PhotoItem, PhotoSingle
from app.services.photos_service import Service  # your Service class

router = APIRouter(prefix="/photos", tags=["photos"])

# single Service instance for the router
service = Service()


@router.post(
    "",
    response_model=dict,  # returns {"id": UUID}; keep exactly as Service.create_photo
    status_code=status.HTTP_201_CREATED,
)
async def create_photo(payload: PhotoUpload):
    return await service.create_photo(payload)


@router.get(
    "",
    response_model=List[PhotoItem],
)
async def list_photos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    return await service.list_photos(page=page, limit=limit)


@router.get(
    "/{photo_id}",
    response_model=PhotoSingle,
)
async def get_photo(photo_id: UUID):
    return await service.get_photo(photo_id)


@router.delete(
    "/{photo_id}",
    response_model=dict,  # {"message": "OK"}
)
async def delete_photo(photo_id: UUID):
    return await service.delete_photo(photo_id)


@router.delete(
    "/latest",
    response_model=dict,  # {"message": "OK"}
)
async def delete_latest():
    return await service.delete_latest()


@router.get(
    "/raw/{photo_id}",
    responses={200: {"content": {"image/png": {}}}},
)
async def get_photo_raw(photo_id: UUID):
    # Service returns a ready-made Response with image/png
    return await service.get_photo_raw(photo_id)
