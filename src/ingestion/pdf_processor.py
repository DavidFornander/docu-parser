import os
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, input_dir="input", output_dir="output", assets_dir="assets"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.assets_dir = Path(assets_dir)
        
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)

    def process_pdf(self, pdf_path):
        """
        Converts a single PDF to Markdown using Marker.
        """
        pdf_path = Path(pdf_path)
        output_subfolder = self.output_dir / pdf_path.stem
        output_subfolder.mkdir(exist_ok=True)
        
        logger.info(f"Processing PDF: {pdf_path}")
        
        # Command for marker. Based on standard marker usage:
        # marker_single <pdf_path> --output_dir <output_dir>
        # Note: This assumes marker is installed in the environment.
        try:
            command = [
                "marker_single", 
                str(pdf_path), 
                "--output_dir", str(self.output_dir),
                "--batch_multiplier", "2"
            ]
            
            # We use subprocess to call marker CLI
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            logger.info(f"Marker output: {result.stdout}")
            
            # Marker usually creates a folder with the PDF name and a .md file inside
            md_file = self.output_dir / pdf_path.stem / f"{pdf_path.stem}.md"
            if md_file.exists():
                return md_file
            else:
                # Some versions might just put it in the output dir
                potential_md = self.output_dir / f"{pdf_path.stem}.md"
                if potential_md.exists():
                    return potential_md
                raise FileNotFoundError(f"Markdown file not found after processing {pdf_path}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Marker failed for {pdf_path}: {e.stderr}")
            raise
        except FileNotFoundError:
            logger.error("marker_single command not found. Ensure marker-pdf is installed.")
            raise

    def get_all_pdfs(self):
        return list(self.input_dir.glob("*.pdf"))

if __name__ == "__main__":
    processor = PDFProcessor()
    pdfs = processor.get_all_pdfs()
    if not pdfs:
        logger.info("No PDFs found in input directory.")
    else:
        for pdf in pdfs:
            try:
                md_file = processor.process_pdf(pdf)
                logger.info(f"Successfully converted to: {md_file}")
            except Exception as e:
                logger.error(f"Failed to process {pdf}: {e}")
