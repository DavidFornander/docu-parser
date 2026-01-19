import os
import shutil
import aiofiles
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List

app = FastAPI(title="Zero-Loss File Manager")

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "src/web/templates")), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = BASE_DIR / "src/web/templates/index.html"
    async with aiofiles.open(template_path, mode='r') as f:
        content = await f.read()
    return content

@app.get("/api/files/{location}")
async def list_files(location: str):
    """List files in input, output, or logs."""
    if location == "input":
        target_dir = INPUT_DIR
    elif location == "output":
        target_dir = OUTPUT_DIR
    elif location == "logs":
        target_dir = LOGS_DIR
    else:
        raise HTTPException(status_code=400, detail="Invalid location")
    
    files = []
    # Walk for output to handle nested folders (e.g. from chunks)
    # For simplicity, we'll just do top-level or depth=1 for now, 
    # but recursive glob is better for output.
    
    if location == "output":
         # Find all files recursively
         for path in target_dir.rglob("*"):
             if path.is_file() and not path.name.startswith("."):
                 rel_path = path.relative_to(target_dir)
                 files.append({
                     "name": str(rel_path),
                     "size": path.stat().st_size,
                     "modified": path.stat().st_mtime
                 })
    else:
        for path in target_dir.iterdir():
            if path.is_file() and not path.name.startswith("."):
                files.append({
                    "name": path.name,
                    "size": path.stat().st_size,
                    "modified": path.stat().st_mtime
                })
    
    # Sort by modified time descending
    files.sort(key=lambda x: x['modified'], reverse=True)
    return files

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    destination = INPUT_DIR / file.filename
    try:
        async with aiofiles.open(destination, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        return {"filename": file.filename, "status": "uploaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{location}/{filepath:path}")
async def download_file(location: str, filepath: str):
    if location == "input":
        base = INPUT_DIR
    elif location == "output":
        base = OUTPUT_DIR
    elif location == "logs":
        base = LOGS_DIR
    else:
        raise HTTPException(status_code=400, detail="Invalid location")
    
    file_path = base / filepath
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_path, filename=file_path.name)

@app.delete("/api/delete/{location}/{filepath:path}")
async def delete_file(location: str, filepath: str):
    if location == "input":
        base = INPUT_DIR
    elif location == "output":
        base = OUTPUT_DIR
    else:
        raise HTTPException(status_code=400, detail="Invalid location (cannot delete logs)")
    
    file_path = base / filepath
    
    # Security check: prevent directory traversal
    try:
        file_path.resolve().relative_to(base.resolve())
    except ValueError:
         raise HTTPException(status_code=403, detail="Access denied")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        if file_path.is_dir():
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
        return {"status": "deleted", "file": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
