from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from app.storage import get_storage_backend, StorageError

app = FastAPI(title="Upload Mock API", version="0.1.0")

# Loosen CORS for quick testing; tighten later.
#   app.add_middleware(
#       CORSMiddleware,
#       allow_origins=["*"],   # Allow requests from ANY origin (unsafe for prod)
#       allow_methods=["*"],   # Allow all HTTP methods (GET, POST, etc.)
#       allow_headers=["*"],   # Allow all request headers
#   )

storage = get_storage_backend()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    try:
        result = await storage.save(file)
        return JSONResponse(
            {
                "message": "uploaded",
                "filename": result["filename"],
                "backend": result["backend"],
                "url": result["url"],          # mock URL for local; real gs:// when using GCS
                "id": result["id"],
            },
            status_code=201,
        )
    except StorageError as e:
        raise HTTPException(status_code=500, detail=str(e))
