# FastAPI Upload Mock

Simple FastAPI backend that lets you upload files to a local folder (mock for Google Cloud Storage).

## Run
```bash
docker build -t fastapi-upload .
docker run -p 8000:8000 -v $(pwd)/data:/data fastapi-upload
