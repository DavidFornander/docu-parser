# src/worker.py

import time
import json
import os
import signal
import logging
import subprocess
import atexit
from pathlib import Path
from tqdm import tqdm

import torch

from db.db_manager import DBManager
from inference.generator import FlashcardGenerator
from inference.prompts import REPAIR_PROMPT_TEMPLATE
from verification.audit import CoverageAuditor, FactChecker
from utils.logger import setup_logger, console
from config import settings

logger = setup_logger("Worker", log_file=settings.logs_dir / "worker.log")

target_notebook = os.environ.get("TARGET_NOTEBOOK")

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Processing timed out")

class StudyWorker:
    def __init__(self, db_path=None, model_name=None):
        self.db = DBManager(db_path if db_path else settings.db_path)
        self.model_name = model_name if model_name else settings.model_name
        self.generator = None
        self.auditor = None
        self.fact_checker = None
        self.initialized = False
        
        # Register cleanup on exit
        atexit.register(self.cleanup)

    def cleanup(self):
        """Gracefully release GPU memory on exit or restart."""
        if not self.initialized:
            return
            
        logger.info("Cleaning up engines and releasing GPU memory...")
        try:
            if self.generator:
                del self.generator
            if self.auditor:
                del self.auditor
            if self.fact_checker:
                del self.fact_checker
                
            # Force GPU memory cleanup
            if torch.cuda.is_available():
                torch.cuda.synchronize()
                torch.cuda.empty_cache()
                
            logger.info("Cleanup complete.")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            self.initialized = False

    def check_gpu_memory(self):
        """Check available GPU memory in GB."""
        if torch.cuda.is_available():
            total = torch.cuda.get_device_properties(0).total_memory / 1e9
            reserved = torch.cuda.memory_reserved(0) / 1e9
            available = total - reserved
            return available
        return 0.0

    def _mark_all_pending_failed(self):
        """Mark all pending jobs as FAILED when engine permanently crashes."""
        logger.info("Marking all pending jobs as FAILED...")
        pending_jobs = self.db.get_all_pending_chunks(target_notebook)
        failed_count = 0
        for job in pending_jobs:
            try:
                self.db.update_chunk_status(
                    chunk_id=job["chunk_id"],
                    status="FAILED",
                    error_log="vLLM engine failed to initialize after multiple retries",
                    notebook=target_notebook
                )
                failed_count += 1
            except Exception as e:
                logger.error(f"Failed to mark job {job.get('chunk_id', 'unknown')}: {e}")
        logger.info(f"Marked {failed_count} jobs as FAILED.")

    def initialize_engine(self):
        logger.info("[bold cyan]Initializing Inference and Verification Engines...[/]")
        
        # Clean GPU memory before starting - releases any orphaned memory from previous runs
        if torch.cuda.is_available():
            logger.info(f"GPU memory before cleanup: {self.check_gpu_memory():.2f} GB available")
            torch.cuda.empty_cache()
            logger.info(f"GPU memory after cleanup: {self.check_gpu_memory():.2f} GB available")
        
        try:
            # IMPORTANT: Initialize vLLM FIRST when GPU is empty.
            # This ensures vLLM reserves memory before embedding models load.
            # Embedding models only need ~500MB, so they fit in remaining space.
            self.generator = FlashcardGenerator(
                model_name=self.model_name, 
                gpu_memory_utilization=0.7,
                max_model_len=4096
            )
            logger.info("vLLM engine initialized successfully.")
            
            # Now initialize embedding models - they use remaining GPU memory
            self.auditor = CoverageAuditor()
            self.fact_checker = FactChecker()
            
            logger.info("All engines initialized successfully.")
            self.initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize engines: {e}")
            raise

    def run(self):
        # Retry logic with exponential backoff for engine initialization
        max_retries = 3
        base_delay = 10  # seconds - give GPU memory time to settle
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.initialize_engine()
                break  # Success, proceed to main loop
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    delay = base_delay * (2 ** (retry_count - 1))  # Exponential backoff: 10s, 20s
                    logger.error(f"Engine initialization failed ({retry_count}/{max_retries}): {e}")
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.critical(f"Engine failed to initialize after {max_retries} attempts.")
                    logger.critical("Marking all pending jobs as FAILED.")
                    self._mark_all_pending_failed()
                    return
        
        initial_count = self.db.get_pending_count(target_notebook)
        logger.info(f"Worker loop started. [bold cyan]{initial_count}[/] jobs pending.")
        
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
            refresh_per_second=1
        ) as progress:
            task_id = progress.add_task("[cyan]Processing Chunks...", total=initial_count if initial_count > 0 else None)
            signal.signal(signal.SIGALRM, timeout_handler)
            
            idle_count = 0
            consecutive_errors = 0
            max_consecutive_errors = 3
            
            while True:
                job = self.db.get_pending_chunk(target_notebook)
                
                if job:
                    idle_count = 0
                    chunk_id = job["chunk_id"]
                    text = job["source_text"]
                    logger.info(f"Processing chunk: [bold cyan]{chunk_id}[/]")
                    
                    signal.alarm(600)
                    try:
                        # 1. Primary Extraction
                        result = self.generator.generate_cards(text)
                        cards = result.get("flashcards", [])
                        
                        # 2. Coverage Audit (CoV Loop)
                        uncovered, score = self.auditor.audit_coverage(text, cards)
                        
                        if uncovered and score < 0.90:
                            repair_text = "\n".join(uncovered)
                            repair_prompt = REPAIR_PROMPT_TEMPLATE.format(uncovered_text=repair_text)
                            repair_outputs = self.generator.llm.generate([repair_prompt], self.generator.sampling_params)
                            repair_result = self.generator.parse_json_output(repair_outputs[0].outputs[0].text)
                            repair_cards = repair_result.get("flashcards", [])
                            cards.extend(repair_cards)
                            _, final_score = self.auditor.audit_coverage(text, cards)
                            score = final_score

                        # 3. Fact Check
                        verified_cards = []
                        for i, card in enumerate(cards):
                            if self.fact_checker.verify_consistency(card) > 0.4:
                                verified_cards.append(card)
                        cards = verified_cards

                        # 4. Commit
                        self.db.update_chunk_status(
                            chunk_id=chunk_id,
                            status='COMPLETED',
                            output_json=json.dumps({"flashcards": cards}),
                            verification_score=score,
                            notebook=target_notebook
                        )
                        logger.info(f"[{chunk_id}] Completed. [bold green]{len(cards)}[/] cards.")
                        consecutive_errors = 0  # Reset on success

                    except TimeoutException:
                        logger.error(f"Timed out: {chunk_id}")
                        self.db.update_chunk_status(chunk_id=chunk_id, status='FAILED', error_log="Timeout", notebook=target_notebook)
                    except Exception as e:
                        consecutive_errors += 1
                        error_str = str(e).lower()
                        
                        # Detect vLLM engine crashes
                        is_vllm_crash = any([
                            "engine core" in error_str,
                            "died unexpectedly" in error_str,
                            "cuda" in error_str and "error" in error_str,
                            "out of memory" in error_str,
                            "no available memory" in error_str,
                        ])
                        
                        if is_vllm_crash or consecutive_errors >= max_consecutive_errors:
                            logger.error(f"Detected engine crash or consecutive errors ({consecutive_errors}). Attempting recovery...")
                            self.cleanup()
                            time.sleep(5)  # Give GPU memory time to settle
                            
                            try:
                                self.initialize_engine()
                                consecutive_errors = 0
                                logger.info("Engine recovered successfully.")
                                # Re-queue the current job
                                self.db.update_chunk_status(chunk_id=chunk_id, status='PENDING', notebook=target_notebook)
                                continue
                            except Exception as recovery_error:
                                logger.critical(f"Engine recovery failed: {recovery_error}")
                                self._mark_all_pending_failed()
                                return
                        
                        logger.error(f"Error: {e}")
                        self.db.update_chunk_status(chunk_id=chunk_id, status='FAILED', error_log=str(e), notebook=target_notebook)
                    finally:
                        signal.alarm(0)
                    
                    progress.advance(task_id)
                else:
                    idle_count += 1
                    if idle_count >= 2:
                        logger.info("Worker shutting down due to inactivity.")
                        break
                    time.sleep(5)


if __name__ == "__main__":
    # Settings automatically picks up ZERO_MODEL_NAME or overrides from config
    # We can also check raw MODEL_NAME for backward compatibility if needed, 
    # but let's stick to settings priority.
    # However, server.py sets MODEL_NAME env var currently. We should check that or update server.py.
    # For now, let's respect the passed arg or settings.
    override_model = os.getenv("MODEL_NAME")
    final_model = override_model if override_model else settings.model_name
    
    worker = StudyWorker(model_name=final_model)
    try:
        worker.run()
    except KeyboardInterrupt:
        logger.info("Worker stopped.")
