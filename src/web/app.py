import os
import json
import sqlite3
import subprocess
import signal
import shutil
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI(title="Zero-Loss Engine Dashboard")
templates = Jinja2Templates(directory="src/web/templates")

DB_PATH = "study_engine.db"
LOG_PATH = "logs/system_state.jsonl"
INPUT_DIR = Path("input")

# Keep track of background processes and settings
state = {
    "ingestion": None,
    "worker": None,
    "current_model": "Qwen/Qwen2.5-0.5B-Instruct" 
}

MODELS = {
    "speed": "Qwen/Qwen2.5-0.5B-Instruct",
    "mastery": "casperhansen/llama-3-8b-instruct-awq"
}

def get_vram_usage():
    try:
        res = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,nounits,noheader"])
        used, total = res.decode().strip().split(",")
        return f"{used.strip()}MB / {total.strip()}MB"
    except:
        return "N/A (No GPU detected)"

def is_process_running(name):
    proc = state.get(name)
    if proc and proc.poll() is None:
        return True
    return False

def get_db_stats():
    if not os.path.exists(DB_PATH):
        return {}
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT status, COUNT(*) FROM processing_queue GROUP BY status")
        stats = dict(cur.fetchall())
    except:
        stats = {}
    conn.close()
    return stats

def get_recent_logs(n=20):
    if not os.path.exists(LOG_PATH):
        return []
    try:
        with open(LOG_PATH, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - 8192))
            lines = f.read().decode(errors="ignore").splitlines()
            log_data = []
            for line in lines[-n:]:
                try:
                    log_data.append(json.loads(line))
                except: continue
            return log_data
    except:
        return []

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_model": state["current_model"]
    })

@app.post("/settings/model")
async def set_model(request: Request):
    form = await request.form()
    mode = form.get("mode")
    if mode in MODELS:
        state["current_model"] = MODELS[mode]
        if is_process_running("worker"):
            state["worker"].terminate()
            state["worker"] = None
        return HTMLResponse(f"<span class='text-purple-400 font-mono text-[10px] uppercase font-bold tracking-widest'>Engine: {mode}</span>")
    return HTMLResponse("Invalid model", status_code=400)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return HTMLResponse("<script>alert('Only PDF files allowed');</script>", status_code=400)
    
    file_path = INPUT_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return HTMLResponse(f"""
        <div class="bg-green-900/30 border border-green-500/50 p-3 rounded-xl text-xs text-green-400 mb-4 flex items-center justify-between">
            <span>Ready: {file.filename}</span>
            <button hx-post="/run/ingestion" hx-target="this" hx-swap="outerHTML" class="bg-green-600 text-white px-3 py-1 rounded-lg font-bold hover:bg-green-500 transition-colors">Start Extraction</button>
        </div>
    """)

@app.get("/system_status")
async def system_status():
    worker_active = is_process_running("worker")
    vram = get_vram_usage()
    dot_color = "bg-green-500" if worker_active else "bg-red-500"
    status_text = "Worker Active" if worker_active else "Worker Idle"
    
    return HTMLResponse(f"""
        <div class="flex items-center space-x-4">
            <div class="text-right">
                <p class="text-[10px] text-gray-500 uppercase font-bold tracking-wider italic">VRAM Usage</p>
                <p class="text-xs font-mono text-blue-400">{vram}</p>
            </div>
            <div class="h-8 w-[1px] bg-gray-800"></div>
            <div class="flex items-center space-x-2">
                <span class="relative flex h-2 w-2">
                    {"<span class='animate-ping absolute inline-flex h-full w-full rounded-full " + dot_color + " opacity-75'></span>" if worker_active else ""}
                    <span class="relative inline-flex rounded-full h-2 w-2 {dot_color}"></span>
                </span>
                <span class="text-[10px] text-gray-400 uppercase font-bold">{status_text}</span>
            </div>
            <button hx-post="/run/worker" hx-swap="outerHTML" class="ml-4 text-[10px] border border-gray-700 px-3 py-1 rounded-full hover:bg-gray-800 transition-colors uppercase font-bold tracking-widest">
                {"Stop Worker" if worker_active else "Start Worker"}
            </button>
        </div>
    """)

@app.get("/chunk/{chunk_id}")
async def get_chunk_details(chunk_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT output_json FROM processing_queue WHERE chunk_id = ?", (chunk_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row or not row[0]:
        return HTMLResponse("<p class='p-4 text-gray-500 text-xs italic text-center mt-10'>No cards available yet.</p>")
    
    data = json.loads(row[0])
    cards = data.get("flashcards", [])
    
    html = f'<div class="p-4 space-y-4 max-h-[350px] overflow-y-auto custom-scrollbar">'
    for i, card in enumerate(cards):
        card_id = f"{chunk_id}_{i}"
        html += f'''
            <div class="bg-gray-900/50 p-3 rounded-xl border border-gray-800 group transition-all" id="card-container-{card_id}">
                <div class="flex justify-between items-start mb-2">
                    <span class="text-[9px] bg-blue-900/20 px-1.5 py-0.5 rounded border border-blue-500/20 text-blue-400 uppercase font-bold tracking-tighter">{card.get("type", "concept")}</span>
                    <div class="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button hx-get="/card/edit/{chunk_id}/{i}" hx-target="#card-container-{card_id}" class="text-[9px] text-gray-500 hover:text-white uppercase font-bold">Edit</button>
                        <button hx-get="/card/delete/{chunk_id}/{i}" 
                                hx-confirm="Are you sure you want to delete this card?"
                                hx-target="#chunk-details" 
                                class="text-[9px] text-red-900 hover:text-red-500 uppercase font-bold">Delete</button>
                    </div>
                </div>
                <p class="font-bold text-xs text-gray-200 mb-1">{card.get("front")}</p>
                <p class="text-xs text-gray-500 leading-relaxed italic line-clamp-2">"{card.get("back")}"</p>
            </div>
        '''
    html += '</div>'
    return HTMLResponse(html)

@app.get("/card/edit/{chunk_id}/{index}")
async def edit_card(chunk_id: str, index: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT output_json FROM processing_queue WHERE chunk_id = ?", (chunk_id,))
    row = cur.fetchone()
    conn.close()
    cards = json.loads(row[0]).get("flashcards", [])
    card = cards[index]
    return HTMLResponse(f"""
        <form hx-post="/card/save/{chunk_id}/{index}" class="space-y-3 bg-[#0d1117] p-3 rounded-xl border border-blue-500 shadow-2xl scale-[1.02] transition-transform">
            <div>
                <label class="text-[8px] text-blue-500 uppercase font-bold mb-1 block">Front</label>
                <textarea name="front" class="w-full bg-black border border-gray-800 rounded-lg p-2 text-xs text-white focus:border-blue-500 outline-none transition-colors" rows="2">{card.get('front')}</textarea>
            </div>
            <div>
                <label class="text-[8px] text-blue-500 uppercase font-bold mb-1 block">Back</label>
                <textarea name="back" class="w-full bg-black border border-gray-800 rounded-lg p-2 text-xs text-white focus:border-blue-500 outline-none transition-colors" rows="2">{card.get('back')}</textarea>
            </div>
            <div class="flex justify-end space-x-2">
                <button type="button" hx-get="/chunk/{chunk_id}" hx-target="#chunk-details" class="text-[9px] text-gray-500 hover:text-white uppercase font-bold">Cancel</button>
                <button type="submit" class="text-[9px] bg-blue-600 hover:bg-blue-500 text-white px-3 py-1 rounded-full font-bold uppercase tracking-widest transition-colors">Apply</button>
            </div>
        </form>
    """)

@app.post("/card/save/{chunk_id}/{index}")
async def save_card(chunk_id: str, index: int, request: Request):
    form = await request.form()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT output_json FROM processing_queue WHERE chunk_id = ?", (chunk_id,))
    row = cur.fetchone()
    data = json.loads(row[0])
    data["flashcards"][index]["front"] = form.get("front")
    data["flashcards"][index]["back"] = form.get("back")
    cur.execute("UPDATE processing_queue SET output_json = ? WHERE chunk_id = ?", (json.dumps(data), chunk_id))
    conn.commit()
    conn.close()
    return await get_chunk_details(chunk_id)

@app.get("/card/delete/{chunk_id}/{index}")
async def delete_card(chunk_id: str, index: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT output_json FROM processing_queue WHERE chunk_id = ?", (chunk_id,))
    row = cur.fetchone()
    data = json.loads(row[0])
    if 0 <= index < len(data["flashcards"]):
        data["flashcards"].pop(index)
    cur.execute("UPDATE processing_queue SET output_json = ? WHERE chunk_id = ?", (json.dumps(data), chunk_id))
    conn.commit()
    conn.close()
    return await get_chunk_details(chunk_id)

@app.get("/stats")
async def stats():
    stats = get_db_stats()
    total = sum(stats.values())
    completed = stats.get('COMPLETED', 0)
    percent = (completed / total * 100) if total > 0 else 0
    return HTMLResponse(f"""
        <div class="grid grid-cols-3 gap-4 text-center">
            <div class="bg-blue-900/20 border border-blue-500/20 p-3 rounded-xl">
                <p class="text-[8px] text-blue-500 uppercase font-bold tracking-widest">Pending</p>
                <p class="text-xl font-mono text-blue-200">{stats.get('PENDING', 0)}</p>
            </div>
            <div class="bg-yellow-900/20 border border-yellow-500/20 p-3 rounded-xl">
                <p class="text-[8px] text-yellow-500 uppercase font-bold tracking-widest">Active</p>
                <p class="text-xl font-mono text-yellow-200">{stats.get('PROCESSING', 0)}</p>
            </div>
            <div class="bg-green-900/20 border border-green-500/20 p-3 rounded-xl">
                <p class="text-[8px] text-green-500 uppercase font-bold tracking-widest">Done</p>
                <p class="text-xl font-mono text-green-200">{completed}</p>
            </div>
        </div>
        <div class="mt-4 bg-gray-800 rounded-full h-1.5 overflow-hidden">
            <div class="bg-blue-500 h-full transition-all duration-1000" style="width: {percent}%"></div>
        </div>
    """)

@app.get("/logs")
async def logs():
    logs = get_recent_logs()
    log_html = ""
    for log in reversed(logs):
        ts = log.get('timestamp', '').split('T')[-1][:8]
        status = log.get('status', 'Unknown')
        color = "text-blue-400" if "Extraction" in status else "text-yellow-400" if "Repairing" in status else "text-gray-500"
        log_html += f'<div class="font-mono text-[10px] border-b border-gray-900 py-1.5 opacity-80"><span class="text-gray-600 mr-2">[{ts}]</span> <span class="{color}">{status}</span></div>'
    return HTMLResponse(log_html)

@app.get("/queue")
async def queue():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT chunk_id, status, verification_score FROM processing_queue ORDER BY updated_at DESC LIMIT 10")
        rows = cur.fetchall()
    except: rows = []
    conn.close()
    html = '<table class="min-w-full text-[10px] text-left"><tbody>'
    for r in rows:
        status_color = "text-green-400" if r[1] == 'COMPLETED' else "text-yellow-400" if r[1] == 'PROCESSING' else "text-red-400" if r[1] == 'FAILED' else "text-gray-600"
        html += f'''
            <tr class="border-b border-gray-800 hover:bg-gray-800/30 cursor-pointer transition-colors" hx-get="/chunk/{r[0]}" hx-target="#chunk-details">
                <td class="p-3 font-mono text-gray-500">{r[0][:8]}</td>
                <td class="p-3 uppercase font-bold {status_color}">{r[1]}</td>
                <td class="p-3 text-right text-gray-400">{f"{r[2]:.2f}" if r[2] else "-"}</td>
            </tr>
        '''
    html += '</tbody></table>'
    return HTMLResponse(html)

@app.get("/export")
async def export():
    output_dir = Path("output")
    files = list(output_dir.glob("*.apkg"))
    if not files: return HTMLResponse("<p class='text-[10px] text-gray-600 italic text-center py-4 uppercase font-bold tracking-widest'>No decks ready</p>")
    html = '<ul class="space-y-2">'
    for f in files:
        html += f'''
            <li class="flex justify-between items-center bg-black/40 p-3 rounded-xl border border-gray-800">
                <span class="text-xs font-mono text-gray-400">{f.name}</span>
                <a href="/download/{f.name}" class="text-[9px] bg-blue-600/20 text-blue-400 border border-blue-500/30 py-1 px-3 rounded-full font-bold uppercase tracking-widest hover:bg-blue-600 hover:text-white transition-all">Get</a>
            </li>
        '''
    html += '</ul>'
    return HTMLResponse(html)

@app.get("/download/{filename}")
async def download(filename: str):
    return FileResponse(path=Path("output") / filename, filename=filename)

@app.post("/run/export")
async def trigger_export():
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}:{os.getcwd()}/src"
    try:
        subprocess.run(["python", "src/utils/exporter.py"], env=env, check=True)
        return HTMLResponse("<span class='text-green-400 font-bold text-xs'>✓ Export Success</span>")
    except Exception as e:
        return HTMLResponse(f"<span class='text-red-400 text-xs font-bold'>✗ Error: {e}</span>")

@app.post("/run/nuke")
async def nuke_system():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM processing_queue")
        conn.commit()
    except: pass
    conn.close()
    for folder in [INPUT_DIR, Path("output"), Path("assets")]:
        for item in folder.iterdir():
            if item.name == ".gitkeep": continue
            if item.is_dir(): shutil.rmtree(item)
            else: item.unlink()
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f: f.write("")
    return HTMLResponse("<script>window.location.reload();</script>")

@app.post("/run/{action}")
async def run_process(action: str):
    if action == "ingestion":
        if is_process_running("ingestion"): return HTMLResponse("Running", status_code=400)
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}:{os.getcwd()}/src"
        state["ingestion"] = subprocess.Popen(["python", "src/main.py"], env=env)
        return HTMLResponse("<span class='text-blue-400 animate-pulse font-bold'>Extraction Active</span>")
    elif action == "worker":
        if is_process_running("worker"):
            # Use process group kill to ensure all sub-processes (vLLM) die
            os.killpg(os.getpgid(state["worker"].pid), signal.SIGTERM)
            state["worker"] = None
            return await system_status()
        
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}:{os.getcwd()}/src"
        env["MODEL_NAME"] = state["current_model"]
        
        # Start in a new process group
        state["worker"] = subprocess.Popen(
            ["python", "src/worker.py"], 
            env=env,
            preexec_fn=os.setsid
        )
        return await system_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)