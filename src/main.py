import logging
import sys
from pathlib import Path
from ingestion.pdf_processor import PDFProcessor
from ingestion.chunker import SemanticChunker
from db.db_manager import DBManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("StudyEngine")

def main():
    # Initialize components
    processor = PDFProcessor()
    chunker = SemanticChunker()
    db = DBManager()

    # 1. Scan and Process PDFs
    pdfs = processor.get_all_pdfs()
    if not pdfs:
        logger.info("No PDFs found in input/. Please place documents there.")
        return

    for pdf in pdfs:
        logger.info(f"Step 1: Ingesting {pdf.name}...")
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
            logger.info(f"Step 3: Populating database with {len(chunks)} chunks...")
            for chunk in chunks:
                db.insert_chunk(
                    chunk_id=chunk["chunk_id"],
                    source_text=chunk["content"],
                    metadata=chunk["metadata"]
                )
            
            logger.info(f"Finished processing {pdf.name}")

        except Exception as e:
            logger.error(f"Error processing {pdf}: {e}")

if __name__ == "__main__":
    main()
