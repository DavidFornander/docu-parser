# src/worker.py

import time
import json
import os
import signal
import logging
import subprocess
from pathlib import Path
from tqdm import tqdm
from db.db_manager import DBManager
from inference.generator import FlashcardGenerator
from inference.prompts import REPAIR_PROMPT_TEMPLATE
from verification.audit import CoverageAuditor, FactChecker
from utils.logger import setup_logger, console, heartbeat

# --- NixOS Triton Monkeypatch ---
try:
    # Try to find ptxas dynamically instead of hardcoding
    ptxas_path = subprocess.check_output(["which", "ptxas"], text=True).strip()
    os.environ["PATH"] = f"{os.path.dirname(ptxas_path)}:{os.environ['PATH']}"
    
    import triton.backends.nvidia.driver
    triton.backends.nvidia.driver.libcuda_dirs = lambda: ["/run/opengl-driver/lib"]
except Exception:
    # Fallback to standard path if which fails
    pass
# --------------------------------

logger = setup_logger("Worker")

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Processing timed out")

class StudyWorker:
    def __init__(self, db_path="study_engine.db", model_name="casperhansen/llama-3-8b-instruct-awq"):
        self.db = DBManager(db_path)
        self.model_name = model_name
        self.generator = None
        self.auditor = None
        self.fact_checker = None

    def initialize_engine(self):
        logger.info("[bold cyan]Initializing Inference and Verification Engines...[/]")
        try:
            # We use lower utilization to leave room for embedding models
            self.generator = FlashcardGenerator(model_name=self.model_name, gpu_memory_utilization=0.5)
            self.auditor = CoverageAuditor()
            self.fact_checker = FactChecker()
        except Exception as e:
            logger.error(f"Failed to initialize engines: {e}")
            raise

    def run(self):
        heartbeat.start()
        heartbeat.set_status("Initializing Engine...")
        if not self.generator:
            self.initialize_engine()

        initial_count = self.db.get_pending_count()
        logger.info(f"Worker loop started. [bold cyan]{initial_count}[/] jobs pending.")
        
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task_id = progress.add_task("[cyan]Processing Chunks...", total=initial_count if initial_count > 0 else None)
            signal.signal(signal.SIGALRM, timeout_handler)
            
            idle_count = 0
            while True:
                heartbeat.set_status("Waiting for jobs...")
                job = self.db.get_pending_chunk()
                
                if job:
                    idle_count = 0
                    chunk_id = job["chunk_id"]
                    text = job["source_text"]
                    logger.info(f"Processing chunk: [bold cyan]{chunk_id}[/]")
                    
                    signal.alarm(600)
                    try:
                        # 1. Primary Extraction
                        heartbeat.set_status(f"Extraction: {chunk_id[:8]}...")
                        start_time = time.time()
                        result = self.generator.generate_cards(text)
                        cards = result.get("flashcards", [])
                        
                        # 2. Coverage Audit (CoV Loop)
                        heartbeat.set_status(f"Audit: {chunk_id[:8]}...")
                        uncovered, score = self.auditor.audit_coverage(text, cards)
                        
                        if uncovered and score < 0.90:
                            heartbeat.set_status(f"Repairing: {chunk_id[:8]}...")
                            repair_text = "\n".join(uncovered)
                            repair_prompt = REPAIR_PROMPT_TEMPLATE.format(uncovered_text=repair_text)
                            repair_outputs = self.generator.llm.generate([repair_prompt], self.generator.sampling_params)
                            repair_result = self.generator.parse_json_output(repair_outputs[0].outputs[0].text)
                            repair_cards = repair_result.get("flashcards", [])
                            cards.extend(repair_cards)
                            _, final_score = self.auditor.audit_coverage(text, cards)
                            score = final_score

                        # 3. Fact Check
                        heartbeat.set_status(f"Fact Check: {chunk_id[:8]}...")
                        verified_cards = []
                        for card in cards:
                            if self.fact_checker.verify_consistency(card) > 0.4:
                                verified_cards.append(card)
                        cards = verified_cards

                        # 4. Commit
                        self.db.update_chunk_status(
                            chunk_id=chunk_id,
                            status='COMPLETED',
                            output_json=json.dumps({"flashcards": cards}),
                            verification_score=score
                        )
                        logger.info(f"[{chunk_id}] Completed. [bold green]{len(cards)}[/] cards.")

                    except TimeoutException:
                        logger.error(f"Timed out: {chunk_id}")
                        self.db.update_chunk_status(chunk_id=chunk_id, status='FAILED', error_log="Timeout")
                    except Exception as e:
                        logger.error(f"Error: {e}")
                        self.db.update_chunk_status(chunk_id=chunk_id, status='FAILED', error_log=str(e))
                    finally:
                        signal.alarm(0)
                    
                    progress.advance(task_id)
                else:
                    heartbeat.set_status("Idle...")
                    time.sleep(5)
                    idle_count += 1
                    if idle_count >= 3:
                        break
        
        heartbeat.stop()

if __name__ == "__main__":
    MODEL = os.getenv("MODEL_NAME", "casperhansen/llama-3-8b-instruct-awq")
    worker = StudyWorker(model_name=MODEL)
    try:
        worker.run()
    except KeyboardInterrupt:
        logger.info("Worker stopped.")
