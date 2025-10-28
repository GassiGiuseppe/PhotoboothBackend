from pydantic import BaseModel
from uuid import UUID

class PhotoUpload(BaseModel):
    # base64-encoded PNG bytes
    data: str

class PhotoItem(BaseModel):
    id: UUID
    url: str

class PhotoSingle(BaseModel):
    id: UUID
    url: str
