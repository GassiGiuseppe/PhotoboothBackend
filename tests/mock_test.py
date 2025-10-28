#!/usr/bin/env python3
import base64
import os
import sys
from urllib.parse import urljoin

import requests

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Tiny 1x1 red PNG (base64) so you don't need any files/deps.
EMBEDDED_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
    "/w8AAwMB/ak1hJkAAAAASUVORK5CYII="
)

def post_photo(b64: str):
    print("\nnew test")
    url = f"{BASE_URL}/photos"
    res = requests.post(url, json={"data": b64})
    print("POST /photos ->", res.status_code, res.text)
    res.raise_for_status()
    return res.json()["id"]

def list_photos(page: int = 1, limit: int = 10):
    print("\nnew test")
    url = f"{BASE_URL}/photos"
    res = requests.get(url, params={"page": page, "limit": limit})
    print(f"GET /photos?page={page}&limit={limit} ->", res.status_code)
    res.raise_for_status()
    return res.json()

def get_photo(photo_id: str):
    print("\nnew test")
    url = f"{BASE_URL}/photos/{photo_id}"
    res = requests.get(url)
    print(f"GET /photos/{photo_id} ->", res.status_code, res.text)
    res.raise_for_status()
    return res.json()

def download_raw(raw_url: str, out_path: str):
    print("\nnew test")
    # raw_url may be relative (e.g., /photos/raw/<id>)
    full = urljoin(BASE_URL, raw_url)
    r = requests.get(full, stream=True)
    print(f"GET {raw_url} (raw) ->", r.status_code)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return out_path

def delete_photo(photo_id: str):
    print("\nnew test")
    url = f"{BASE_URL}/photos/{photo_id}"
    res = requests.delete(url)
    print(f"DELETE /photos/{photo_id} ->", res.status_code, res.text)
    # 200 expected; 404 means it was already gone
    if res.status_code not in (200, 404):
        res.raise_for_status()
    return res.status_code

def delete_latest():
    print("\nnew test")
    url = f"{BASE_URL}/photos/latest"
    res = requests.delete(url)
    print("DELETE /photos/latest ->", res.status_code, res.text)
    return res.status_code

def load_png_b64_from_file(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

def main():
    # optionally allow: python mock_test.py /path/to/image.png
    test_path = "./tests/test.png"

    # Always prefer the local test image if it exists
    if os.path.isfile(test_path):
        b64 = load_png_b64_from_file(test_path)
        print(f"Using PNG from file: {test_path}")
    else:
        b64 = EMBEDDED_PNG_B64
        print("Using embedded 1x1 PNG (no ./tests/test.png found)")

    # 1) upload
    photo_id = post_photo(b64)
    print("New photo id:", photo_id)

    # 2) list (page 1)
    items = list_photos(page=1, limit=10)
    print("Listed items:", items)

    # 3) get one
    detail = get_photo(photo_id)
    signed_url = detail["url"]
    print("Signed URL:", signed_url)

    # 4) download raw
    out_file = download_raw(signed_url, f"./downloaded_{photo_id}.png")
    print("Downloaded to:", out_file)

    # 5) delete the photo
    delete_photo(photo_id)

    # 6) optional: delete latest (uncomment to try)
    # delete_latest()

    # 7) list again to confirm
    items2 = list_photos(page=1, limit=10)
    print("After deletion, items:", items2)

if __name__ == "__main__":
    main()
