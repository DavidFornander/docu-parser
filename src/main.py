import sys
import subprocess
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from ingestion.pdf_processor import PDFProcessor
from ingestion.chunker import SemanticChunker
from db.db_manager import DBManager
from utils.logger import setup_logger, console, heartbeat

logger = setup_logger("StudyEngine")

def check_environment():
    heartbeat.set_status("Checking environment...")
    """Performs a pre-flight check of critical dependencies."""
    logger.info("Performing environment pre-flight check...")
    try:
        # Check standard imports
        import numpy
        import torch
        logger.info(f"NumPy version: {numpy.__version__}")
        logger.info(f"Torch version: {torch.__version__}")
        
        # Check marker command
        result = subprocess.run(["marker_single", "--help"], capture_output=True, text=True)
        if result.returncode != 0 and "usage" not in result.stdout and "usage" not in result.stderr:
             # Some CLIs return non-zero on help, but usually print usage. 
             # If completely broken (like ImportError), it won't print usage.
             if "ImportError" in result.stderr:
                 logger.error(f"Marker CLI is broken: {result.stderr.strip()}")
                 return False
        
        logger.info("Environment check passed.")
        return True
    except ImportError as e:
        logger.error(f"Critical dependency missing: {e}")
        return False
    except FileNotFoundError:
        logger.error("marker_single command not found in PATH.")
        return False
    except Exception as e:
        logger.error(f"Environment check failed: {e}")
        return False

def main():
    heartbeat.start()
    if not check_environment():
        logger.error("Environment check failed. Exiting.")
        heartbeat.stop()
        sys.exit(1)

    # Initialize components
    heartbeat.set_status("Initializing components...")
    processor = PDFProcessor()
    chunker = SemanticChunker()
    db = DBManager()

    # 1. Scan and Process PDFs
    pdfs = processor.get_all_pdfs()
    if not pdfs:
        logger.warning("No PDFs found in input/. Please place documents there.")
        heartbeat.stop()
        return

    logger.info("Starting ingestion pipeline...")
    
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
            heartbeat.set_status(f"Ingesting PDF: {pdf.name}")
            try:
                # Note: This calls Marker CLI. Ensure it's installed.
                md_file_path = processor.process_pdf(pdf)
                
                # Read the generated markdown
                with open(md_file_path, "r", encoding="utf-8") as f:
                    markdown_content = f.read()

                # 2. Chunking
                logger.info(f"Step 2: Chunking {pdf.name}...")
                heartbeat.set_status(f"Chunking: {pdf.name}")
                metadata = {"source_file": pdf.name, "path": str(pdf)}
                chunks = chunker.chunk_text(markdown_content, metadata=metadata)

                # 3. Populate Database
                logger.info(f"Step 3: Populating database with [bold green]{len(chunks)}[/] chunks...")
                heartbeat.set_status(f"Saving {len(chunks)} chunks to DB")
                
                chunk_task = progress.add_task(f"Inserting chunks for {pdf.name}", total=len(chunks))
                for chunk in chunks:
                    db.insert_chunk(
                        chunk_id=chunk["chunk_id"],
                        source_text=chunk["content"],
                        metadata=chunk["metadata"]
                    )
                    progress.advance(chunk_task)
                
                progress.remove_task(chunk_task)
                logger.info(f"Finished processing [bold green]{pdf.name}[/]")

            except Exception as e:
                logger.error(f"Error processing {pdf}: {e}")
            
            progress.advance(pdf_task)
    
    heartbeat.set_status("Done")
    heartbeat.stop()

if __name__ == "__main__":
    main()
