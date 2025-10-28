# app/main.py
import os
from fastapi import FastAPI

# include the photos router you just rewrote
from app.routers.photos import router as photos_router
from app.storage.local_ids_db.adapter import PhotoIndexAsync

app = FastAPI(title="Photo API", version="0.1.0")

# ---- optional CORS for local frontend testing (uncomment if needed) ----
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# include routes
app.include_router(photos_router)

# simple healthcheck
@app.get("/health")
async def health():
    return {"status": "ok"}

# ---- optional: tidy engine lifecycle (nice to have) ----
# If you want to cleanly dispose the SQLAlchemy async engine on shutdown,
# import the shared instance from the router OR create one here and pass it in.
# Below we reference the same DATABASE_URL and create a tiny disposable handle.
DATABASE_URL = os.getenv("DATABASE_URL")

_index_engine = None
if DATABASE_URL:
    _index_engine = PhotoIndexAsync(DATABASE_URL)  # a throwaway handle just to dispose engine

@app.on_event("shutdown")
async def shutdown():
    if _index_engine:
        await _index_engine.engine.dispose()
