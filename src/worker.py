# src/worker.py

import time
import json
import logging
import os
from db.db_manager import DBManager
from inference.generator import FlashcardGenerator
from inference.prompts import REPAIR_PROMPT_TEMPLATE
from verification.audit import CoverageAuditor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Worker")

class StudyWorker:
    def __init__(self, db_path="study_engine.db", model_name="casperhansen/llama-3-8b-instruct-awq"):
        self.db = DBManager(db_path)
        self.model_name = model_name
        self.generator = None
        self.auditor = None

    def initialize_engine(self):
        logger.info("Initializing Inference and Verification Engines...")
        try:
            self.generator = FlashcardGenerator(model_name=self.model_name)
            self.auditor = CoverageAuditor()
        except Exception as e:
            logger.error(f"Failed to initialize engines: {e}")
            raise

    def run(self):
        if not self.generator:
            self.initialize_engine()

        logger.info("Worker loop started. Waiting for jobs...")
        
        while True:
            job = self.db.get_pending_chunk()
            
            if job:
                chunk_id = job["chunk_id"]
                text = job["source_text"]
                logger.info(f"Processing chunk: {chunk_id}")
                
                try:
                    # 1. Primary Extraction
                    start_time = time.time()
                    result = self.generator.generate_cards(text)
                    cards = result.get("flashcards", [])
                    
                    # 2. Coverage Audit (CoV Loop)
                    uncovered, score = self.auditor.audit_coverage(text, cards)
                    logger.info(f"Initial coverage score: {score:.2f}")
                    
                    if uncovered and score < 0.90:
                        logger.info(f"Triggering Chain of Verification for {len(uncovered)} sentences...")
                        repair_text = "\n".join(uncovered)
                        repair_prompt = REPAIR_PROMPT_TEMPLATE.format(uncovered_text=repair_text)
                        
                        # Generate repair cards
                        repair_outputs = self.generator.llm.generate([repair_prompt], self.generator.sampling_params)
                        repair_result = self.generator.parse_json_output(repair_outputs[0].outputs[0].text)
                        
                        repair_cards = repair_result.get("flashcards", [])
                        logger.info(f"Generated {len(repair_cards)} repair cards.")
                        cards.extend(repair_cards)
                        
                        # Final audit
                        _, final_score = self.auditor.audit_coverage(text, cards)
                        score = final_score
                        logger.info(f"Final coverage score: {score:.2f}")

                    # 3. Commit
                    duration = time.time() - start_time
                    if cards:
                        logger.info(f"Generated {len(cards)} total cards in {duration:.2f}s")
                        self.db.update_chunk_status(
                            chunk_id=chunk_id,
                            status='COMPLETED',
                            output_json=json.dumps({"flashcards": cards}),
                            verification_score=score
                        )
                    else:
                        logger.warning(f"No cards generated for chunk {chunk_id}")
                        self.db.update_chunk_status(
                            chunk_id=chunk_id,
                            status='FAILED',
                            error_log="No flashcards generated or parsing failed"
                        )
                
                except Exception as e:
                    logger.error(f"Error processing chunk {chunk_id}: {e}")
                    self.db.update_chunk_status(
                        chunk_id=chunk_id,
                        status='FAILED',
                        error_log=str(e)
                    )
            else:
                time.sleep(5)

if __name__ == "__main__":
    # You can specify the model via environment variable or CLI argument
    # Defaulting to an AWQ model for 12GB VRAM compatibility
    MODEL = os.getenv("MODEL_NAME", "casperhansen/llama-3-8b-instruct-awq")
    worker = StudyWorker(model_name=MODEL)
    try:
        worker.run()
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")
