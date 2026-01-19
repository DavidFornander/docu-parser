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
from utils.logger import setup_logger, console
from config import settings

logger = setup_logger("Worker", log_file=settings.logs_dir / "worker.log")

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

    def initialize_engine(self):
        logger.info("[bold cyan]Initializing Inference and Verification Engines...[/]")
        try:
            # Utilization 0.7 leaves room for Embeddings and Cross-Encoders.
            self.generator = FlashcardGenerator(
                model_name=self.model_name, 
                gpu_memory_utilization=0.7,
                max_model_len=4096
            )
            self.auditor = CoverageAuditor()
            self.fact_checker = FactChecker()
        except Exception as e:
            logger.error(f"Failed to initialize engines: {e}")
            raise

    def run(self):
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
            console=console,
            refresh_per_second=1
        ) as progress:
            task_id = progress.add_task("[cyan]Processing Chunks...", total=initial_count if initial_count > 0 else None)
            signal.signal(signal.SIGALRM, timeout_handler)
            
            idle_count = 0
            while True:
                job = self.db.get_pending_chunk()
                
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
