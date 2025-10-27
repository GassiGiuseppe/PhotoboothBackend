from dataclasses import dataclass
from datetime import datetime

@dataclass
class Photo:
    id: str               # uuid string
    filename: str         # original client filename, e.g. foo.png
    content_type: str     # "image/png"
    size_bytes: int
    storage_key: str      # "photos/<uuid>.png" (or your chosen layout)
    created_at: datetime
