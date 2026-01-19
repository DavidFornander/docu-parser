import os
import shutil
import aiofiles
import subprocess
import asyncio
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from pydantic import BaseModel
from config import settings

app = FastAPI(title="Zero-Loss File Manager")

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent
INPUT_DIR = settings.input_dir
OUTPUT_DIR = settings.output_dir
LOGS_DIR = settings.logs_dir

# Directories are created by settings properties, but let's double check/ensure
# settings.input_dir.mkdir(...) happens when accessed? 
# Yes, property does it. Calling them above triggers creation.

class PipelineRequest(BaseModel):
    model_name: str
    notebook: Optional[str] = None

class NotebookRequest(BaseModel):
    name: str

async def run_pipeline_task(model_name: str, notebook: Optional[str] = None):
    """
    Runs the pipeline steps sequentially in the background.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}:{BASE_DIR}/src"
    env["MODEL_NAME"] = model_name
    if notebook:
        env["TARGET_NOTEBOOK"] = notebook
    
    # We log to a specific file so the user can potentially see it (not implemented in UI yet)
    # or just to the standard logs.
    
    cmd = (
        f"python3 src/ingestor.py && "
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
    background_tasks.add_task(run_pipeline_task, request.model_name, request.notebook)
    return {"status": "started", "model": request.model_name, "notebook": request.notebook}

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

@app.post("/api/notebooks")
async def create_notebook(request: NotebookRequest):
    """Creates a new notebook (subfolder) in the input directory."""
    notebook_path = INPUT_DIR / request.name
    try:
        if notebook_path.exists():
             raise HTTPException(status_code=400, detail="Notebook already exists")
        notebook_path.mkdir(parents=True)
        return {"status": "created", "name": request.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/notebooks/{name}")
async def delete_notebook(name: str):
    """Deletes a notebook (subfolder) and its contents."""
    notebook_path = INPUT_DIR / name
    
    # Security check
    try:
        notebook_path.resolve().relative_to(INPUT_DIR.resolve())
    except ValueError:
         raise HTTPException(status_code=403, detail="Access denied")

    if not notebook_path.exists():
        raise HTTPException(status_code=404, detail="Notebook not found")
        
    try:
        shutil.rmtree(notebook_path)
        return {"status": "deleted", "name": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/{location}")
async def list_files(location: str, notebook: Optional[str] = None):
    """List files in input, output, logs, or list notebooks."""
    if location == "notebooks":
        # List subdirectories in input
        dirs = []
        for path in INPUT_DIR.iterdir():
            if path.is_dir() and not path.name.startswith("."):
                dirs.append({
                    "name": path.name,
                    "modified": path.stat().st_mtime
                })
        dirs.sort(key=lambda x: x['name']) # Sort alphabetically
        return dirs

    if location == "input":
        target_dir = INPUT_DIR
        if notebook:
            target_dir = INPUT_DIR / notebook
    elif location == "output":
        target_dir = OUTPUT_DIR
        if notebook:
            target_dir = OUTPUT_DIR / notebook
    elif location == "logs":
        target_dir = LOGS_DIR
    else:
        raise HTTPException(status_code=400, detail="Invalid location")
    
    # If notebook dir doesn't exist yet, return empty
    if not target_dir.exists():
        return []
        
    files = []
    
    # For output, we might still want recursive search if there are subfolders like 'chunks'
    # But usually CSVs are at the top of the notebook output folder.
    if location == "output":
         for path in target_dir.rglob("*"):
             if path.is_file() and not path.name.startswith("."):
                 try:
                    rel_path = path.relative_to(target_dir)
                    files.append({
                        "name": str(rel_path),
                        "size": path.stat().st_size,
                        "modified": path.stat().st_mtime
                    })
                 except ValueError:
                     continue
    else:
        # For input/logs, list direct files
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
async def upload_file(file: UploadFile = File(...), notebook: Optional[str] = Form(None)):
    if notebook:
        destination_dir = INPUT_DIR / notebook
        destination_dir.mkdir(exist_ok=True)
        destination = destination_dir / file.filename
    else:
        destination = INPUT_DIR / file.filename
        
    try:
        async with aiofiles.open(destination, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        return {"filename": file.filename, "status": "uploaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{location}/{filepath:path}")
async def download_file(location: str, filepath: str, notebook: Optional[str] = None):
    if location == "input":
        base = INPUT_DIR / notebook if notebook else INPUT_DIR
    elif location == "output":
        base = OUTPUT_DIR / notebook if notebook else OUTPUT_DIR
    elif location == "logs":
        base = LOGS_DIR
    else:
        raise HTTPException(status_code=400, detail="Invalid location")
    
    file_path = base / filepath
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_path, filename=file_path.name)

@app.delete("/api/delete/{location}/{filepath:path}")
async def delete_file(location: str, filepath: str, notebook: Optional[str] = None):
    if location == "input":
        base = INPUT_DIR / notebook if notebook else INPUT_DIR
    elif location == "output":
        base = OUTPUT_DIR / notebook if notebook else OUTPUT_DIR
    else:
        raise HTTPException(status_code=400, detail="Invalid location (cannot delete logs)")
    
    file_path = base / filepath
    
    # Security check: prevent directory traversal
    try:
        # Resolve base properly
        resolved_base = (INPUT_DIR if location == "input" else OUTPUT_DIR).resolve()
        file_path.resolve().relative_to(resolved_base)
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
async def delete_all_files(location: str, notebook: Optional[str] = None):
    if location == "input":
        target_dir = INPUT_DIR / notebook if notebook else INPUT_DIR
    elif location == "output":
        target_dir = OUTPUT_DIR / notebook if notebook else OUTPUT_DIR
    else:
        raise HTTPException(status_code=400, detail="Invalid location")
    
    if not target_dir.exists():
         return {"status": "cleared", "location": location}

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
