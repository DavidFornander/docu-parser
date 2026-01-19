import os
import shutil
import aiofiles
import subprocess
import asyncio
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(title="Zero-Loss File Manager")

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class PipelineRequest(BaseModel):
    model_name: str

async def run_pipeline_task(model_name: str):
    """
    Runs the pipeline steps sequentially in the background.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}:{BASE_DIR}/src"
    env["MODEL_NAME"] = model_name
    
    # We log to a specific file so the user can potentially see it (not implemented in UI yet)
    # or just to the standard logs.
    
    cmd = (
        f"python3 src/main.py && "
        f"python3 src/worker.py && "
        f"python3 src/utils/exporter.py"
    )
    
    try:
        # Run as a shell command, redirecting output to pipeline.log
        log_file_path = LOGS_DIR / "pipeline.log"
        with open(log_file_path, "w") as f:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=f,
                stderr=f,
                env=env,
                cwd=str(BASE_DIR)
            )
            await process.communicate()
        
        if process.returncode != 0:
            print(f"Pipeline failed. Check {log_file_path}")
        else:
            print("Pipeline completed successfully.")
            
    except Exception as e:
        print(f"Error running pipeline: {e}")

@app.post("/api/run")
async def run_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_pipeline_task, request.model_name)
    return {"status": "started", "model": request.model_name}

@app.get("/api/logs/content/{filename}")
async def get_log_content(filename: str):
    """
    Returns the tail content of a specific log file.
    """
    log_path = LOGS_DIR / filename
    
    # Security check
    try:
        log_path.resolve().relative_to(LOGS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
        
    if not log_path.exists():
        return {"content": "(Log file empty or does not exist yet)"}
        
    try:
        # Read last 50KB to avoid sending too much data
        file_size = log_path.stat().st_size
        read_size = min(file_size, 50 * 1024)
        
        async with aiofiles.open(log_path, mode='r', encoding='utf-8', errors='replace') as f:
            if file_size > read_size:
                await f.seek(file_size - read_size)
            content = await f.read()
            return {"content": content}
    except Exception as e:
        return {"content": f"Error reading log: {str(e)}"}

@app.get("/api/system_stats")
async def get_system_stats():
    """
    Returns GPU memory usage if available.
    """
    vram_used = 0
    vram_total = 0
    gpu_name = "N/A"
    
    try:
        # Check if nvidia-smi exists
        if shutil.which("nvidia-smi"):
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.total,name", "--format=csv,noheader,nounits"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    # Parse first GPU
                    parts = output.split(',')
                    if len(parts) >= 3:
                        vram_used = float(parts[0].strip())
                        vram_total = float(parts[1].strip())
                        gpu_name = parts[2].strip()
    except Exception as e:
        print(f"Error checking GPU stats: {e}")
        
    return {
        "vram_used_mb": vram_used,
        "vram_total_mb": vram_total,
        "gpu_name": gpu_name
    }

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

@app.delete("/api/delete_all/{location}")
async def delete_all_files(location: str):
    if location == "input":
        target_dir = INPUT_DIR
    elif location == "output":
        target_dir = OUTPUT_DIR
    else:
        raise HTTPException(status_code=400, detail="Invalid location")
    
    try:
        for item in target_dir.iterdir():
            if item.name == ".gitkeep":
                continue
            if item.is_file():
                os.remove(item)
            elif item.is_dir():
                shutil.rmtree(item)
        return {"status": "cleared", "location": location}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
