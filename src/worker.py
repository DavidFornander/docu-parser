# src/worker.py

import time
import json
import os
import signal
import logging
import subprocess
from pathlib import Path

# --- NixOS Triton Monkeypatch ---
try:
    # 1. Fix ptxas path
    os.environ["PATH"] = f"/nix/store/al5pjd77g5gi541gz5536k1wd8kxg65c-cuda12.8-cuda_nvcc-12.8.93/bin:{os.environ['PATH']}"
    
    # 2. Fix libcuda path
    import triton.backends.nvidia.driver
    def patched_libcuda_dirs():
        return ["/run/opengl-driver/lib"]
    triton.backends.nvidia.driver.libcuda_dirs = patched_libcuda_dirs
except ImportError:
    pass
# --------------------------------

from tqdm import tqdm
from db.db_manager import DBManager
from inference.generator import FlashcardGenerator
from inference.prompts import REPAIR_PROMPT_TEMPLATE
from verification.audit import CoverageAuditor
from utils.logger import setup_logger, console, heartbeat

logger = setup_logger("Worker")

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Processing timed out")

class StudyWorker:
    def __init__(self, db_path="study_engine.db", model_name="Qwen/Qwen2.5-0.5B-Instruct"):
        # Previous model: casperhansen/llama-3-8b-instruct-awq
        self.db = DBManager(db_path)
        self.model_name = model_name
        self.generator = None
        self.auditor = None

    def initialize_engine(self):
        logger.info("[bold cyan]Initializing Inference and Verification Engines...[/]")
        try:
            self.generator = FlashcardGenerator(model_name=self.model_name)
            self.auditor = CoverageAuditor()
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
        
        # We use a progress bar that can be updated dynamically
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:                
            # Create a task with the initial count
            task_id = progress.add_task("[cyan]Processing Chunks...", total=initial_count if initial_count > 0 else None)
            
            # Set signal handler for timeouts
            signal.signal(signal.SIGALRM, timeout_handler)
            
            idle_count = 0
            while True:
                heartbeat.set_status("Waiting for jobs...")
                # 1. Peek & Lock
                job = self.db.get_pending_chunk()
                
                if job:
                    idle_count = 0
                    chunk_id = job["chunk_id"]
                    text = job["source_text"]
                    logger.info(f"Processing chunk: [bold cyan]{chunk_id}[/]")
                    heartbeat.set_status(f"Processing: {chunk_id[:8]}")
                    
                    # Set alarm for 600 seconds (10 minutes)
                    signal.alarm(600)
                    try:
                        # 1. Primary Extraction
                        logger.info(f"[{chunk_id}] Starting [bold]primary extraction[/]...")
                        heartbeat.set_status(f"Extraction: {chunk_id[:8]}...")
                        start_time = time.time()
                        result = self.generator.generate_cards(text)
                        cards = result.get("flashcards", [])
                        inf_duration = time.time() - start_time
                        logger.info(f"[{chunk_id}] Extraction completed: [bold green]{len(cards)}[/] cards found in {inf_duration:.2f}s")
                        
                        # 2. Coverage Audit (CoV Loop)
                        logger.info(f"[{chunk_id}] Starting [bold]coverage audit[/]...")
                        heartbeat.set_status(f"Audit: {chunk_id[:8]}...")
                        audit_start = time.time()
                        uncovered, score = self.auditor.audit_coverage(text, cards)
                        audit_duration = time.time() - audit_start
                        logger.info(f"[{chunk_id}] Audit completed in {audit_duration:.2f}s. Initial score: [bold magenta]{score:.2f}[/]")
                        
                        if uncovered and score < 0.90:
                            logger.info(f"[{chunk_id}] Coverage below threshold. Triggering [bold yellow]CoV[/] for {len(uncovered)} sentences...")
                            heartbeat.set_status(f"Repairing: {chunk_id[:8]}...")
                            repair_text = "\n".join(uncovered)
                            repair_prompt = REPAIR_PROMPT_TEMPLATE.format(uncovered_text=repair_text)
                            
                            # Generate repair cards
                            repair_start = time.time()
                            repair_outputs = self.generator.llm.generate([repair_prompt], self.generator.sampling_params)
                            repair_result = self.generator.parse_json_output(repair_outputs[0].outputs[0].text)
                            
                            repair_cards = repair_result.get("flashcards", [])
                            repair_duration = time.time() - repair_start
                            logger.info(f"[{chunk_id}] CoV completed in {repair_duration:.2f}s. Generated [bold green]{len(repair_cards)}[/] repair cards.")
                            cards.extend(repair_cards)
                            
                            # Final audit
                            logger.info(f"[{chunk_id}] Running final audit...")
                            _, final_score = self.auditor.audit_coverage(text, cards)
                            score = final_score
                            logger.info(f"[{chunk_id}] Final coverage score: [bold magenta]{score:.2f}[/]")

                        # 3. Commit
                        heartbeat.set_status(f"Committing: {chunk_id[:8]}")
                        total_duration = time.time() - start_time
                        if cards:
                            logger.info(f"[{chunk_id}] Committing [bold green]{len(cards)}[/] total cards. Total time: {total_duration:.2f}s")
                            self.db.update_chunk_status(
                                chunk_id=chunk_id,
                                status='COMPLETED',
                                output_json=json.dumps({"flashcards": cards}),
                                verification_score=score
                            )
                        else:
                            logger.warning(f"[{chunk_id}] [bold red]No cards generated.[/]")
                            self.db.update_chunk_status(
                                chunk_id=chunk_id,
                                status='FAILED',
                                error_log="No flashcards generated or parsing failed"
                            )

                    except TimeoutException:
                        logger.error(f"Processing timed out for chunk {chunk_id}")
                        self.db.update_chunk_status(
                            chunk_id=chunk_id,
                            status='FAILED',
                            error_log="Processing timed out after 600 seconds"
                        )
                    except Exception as e:
                        logger.error(f"Error processing chunk {chunk_id}: {e}")
                        self.db.update_chunk_status(
                            chunk_id=chunk_id,
                            status='FAILED',
                            error_log=str(e)
                        )
                    finally:
                        # Cancel the alarm
                        signal.alarm(0)
                    
                    progress.advance(task_id)
                else:
                    # No jobs found, sleep for a bit
                    heartbeat.set_status("Idle...")
                    time.sleep(5)
                    idle_count += 1
                    if idle_count >= 3:
                        logger.info("No jobs found for 3 cycles. Exiting worker for test.")
                        break
        
        heartbeat.stop()
if __name__ == "__main__":
    # You can specify the model via environment variable or CLI argument
    # Defaulting to a tiny model for speed and low VRAM footprint
    MODEL = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-0.5B-Instruct")
    # Previous model: casperhansen/llama-3-8b-instruct-awq
    worker = StudyWorker(model_name=MODEL)
    try:
        worker.run()
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")