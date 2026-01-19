import sys
import os
import subprocess
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from ingestion.pdf_processor import PDFProcessor
from ingestion.chunker import SemanticChunker
from db.db_manager import DBManager
from utils.logger import setup_logger, console
from config import settings

logger = setup_logger("StudyEngine", log_file=settings.logs_dir / "ingestion.log")

# Determine Input Directory
target_notebook = os.environ.get("TARGET_NOTEBOOK")
if target_notebook:
    INPUT_DIR = settings.input_dir / target_notebook
    logger.info(f"Targeting specific notebook: {target_notebook}")
else:
    INPUT_DIR = settings.input_dir
    logger.info("Targeting root input directory")

def check_environment():
    """Performs a pre-flight check of critical dependencies."""
    logger.info("Performing environment pre-flight check...")
    try:
        # Check critical imports
        import numpy
        import torch
        import vllm
        from docling.document_converter import DocumentConverter
        
        logger.info(f"NumPy version: {numpy.__version__}")
        logger.info(f"Torch version: {torch.__version__}")
        logger.info(f"vLLM version: {vllm.__version__}")
        
        logger.info("Environment check passed.")
        return True
    except ImportError as e:
        logger.error(f"Critical dependency missing: {e}")
        return False
    except Exception as e:
        logger.error(f"Environment check failed: {e}")
        return False

def main():
    if not check_environment():
        logger.error("Environment check failed. Exiting.")
        sys.exit(1)

    # Initialize components
    processor = PDFProcessor()
    chunker = SemanticChunker()
    db = DBManager()

    # 1. Scan and Register new PDFs
    raw_pdfs = list(INPUT_DIR.glob("*.pdf"))
    for pdf in raw_pdfs:
        db.add_document_to_library(pdf.name)
        # For simplicity in 'run.sh' flow, we move LIBRARY files to PROCESSING
        # In a real UI, this would be triggered by a 'Process' button.
        db.update_document_status(pdf.name, 'PROCESSING')

    # 2. Get files to process
    pdfs_to_process = db.get_documents_by_status('PROCESSING')
    
    if not pdfs_to_process:
        logger.warning("No files in 'PROCESSING' state found in DB or input folder.")
        return

    # Convert filenames to Path objects
    pdfs = [INPUT_DIR / f for f in pdfs_to_process]

    logger.info(f"Starting ingestion pipeline for {len(pdfs)} files...")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console # Use the shared console
    ) as progress:
        
        pdf_task = progress.add_task("[cyan]Processing PDFs...", total=len(pdfs))
        
        for pdf in pdfs:
            logger.info(f"Step 1: Ingesting [bold cyan]{pdf.name}[/]...")
            try:
                # Note: This calls Marker CLI. Ensure it's installed.
                md_file_path = processor.process_pdf(pdf)
                
                # Read the generated markdown
                with open(md_file_path, "r", encoding="utf-8") as f:
                    markdown_content = f.read()

                # 2. Chunking
                logger.info(f"Step 2: Chunking {pdf.name}...")
                metadata = {"source_file": pdf.name, "path": str(pdf)}
                chunks = chunker.chunk_text(markdown_content, metadata=metadata)
                
                # 3. Populate Database
                logger.info(f"Step 3: Populating database with [bold green]{len(chunks)}[/] chunks...")
                
                chunk_task = progress.add_task(f"Inserting chunks for {pdf.name}", total=len(chunks))
                for chunk in chunks:
                    db.insert_chunk(
                        chunk_id=chunk["chunk_id"],
                        source_text=chunk["content"],
                        metadata=chunk["metadata"]
                    )
                    progress.advance(chunk_task)
                
                progress.remove_task(chunk_task)
                
                # MARK AS COMPLETED in documents table
                db.update_document_status(pdf.name, 'COMPLETED')
                
                logger.info(f"Finished processing [bold green]{pdf.name}[/]")

            except Exception as e:
                logger.error(f"Error processing {pdf}: {e}")
            
            progress.advance(pdf_task)
    
if __name__ == "__main__":
    main()
