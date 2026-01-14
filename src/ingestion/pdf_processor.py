import os
import subprocess
import logging
from pathlib import Path
from utils.logger import setup_logger
from inference.vision import ImageDescriber

logger = setup_logger("PDFProcessor")

class PDFProcessor:
    def __init__(self, input_dir="input", output_dir="output", assets_dir="assets"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.assets_dir = Path(assets_dir)
        
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)

    def enrich_with_visuals(self, md_file, assets_folder):
        """
        Scans assets folder for images, describes them, and injects into MD.
        """
        if not assets_folder.exists():
            logger.info(f"No assets folder found at {assets_folder}, skipping visual enrichment.")
            return

        image_files = list(assets_folder.glob("*.png")) + list(assets_folder.glob("*.jpg")) + list(assets_folder.glob("*.jpeg"))
        if not image_files:
            logger.info(f"No images found in {assets_folder}.")
            return

        logger.info(f"Enriching with {len(image_files)} images using VLM...")
        
        try:
            # Load VLM temporarily
            describer = ImageDescriber()
            
            visual_context = "\n\n## Visual Context (Extracted Diagrams)\n"
            for img_path in image_files:
                logger.info(f"Describing image: {img_path.name}")
                description = describer.describe(img_path)
                visual_context += f"\n### Image: {img_path.name}\n{description}\n"
            
            with open(md_file, "a", encoding="utf-8") as f:
                f.write("\n<visual_context>\n" + visual_context + "\n</visual_context>\n")
            
            logger.info("Visual enrichment complete.")
            
            # Explicitly free memory if possible (though process exit handles it)
            del describer
            import torch
            torch.cuda.empty_cache()
            
        except Exception as e:
            logger.error(f"Visual enrichment failed: {e}")

    def process_pdf(self, pdf_path):
        """
        Converts a single PDF to Markdown using Marker.
        """
        pdf_path = Path(pdf_path)
        output_subfolder = self.output_dir / pdf_path.stem
        output_subfolder.mkdir(exist_ok=True)
        
        md_file = output_subfolder / f"{pdf_path.stem}.md"
        if md_file.exists():
            logger.info(f"Markdown already exists for {pdf_path}, skipping conversion.")
            return md_file

        logger.info(f"Processing PDF: {pdf_path}")
        
        # Command for marker. Based on standard marker usage:
        # marker_single <pdf_path> --output_dir <output_dir>
        # Note: This assumes marker is installed in the environment.
        try:
            # Ensure absolute paths
            abs_pdf_path = pdf_path.resolve()
            abs_output_dir = self.output_dir.resolve()
            
            command = [
                "marker_single", 
                str(abs_pdf_path), 
                "--output_dir", str(abs_output_dir)
            ]
            
            # Use Popen to stream output and avoid appearing stuck
            # bufsize=0 and env=os.environ.copy() are CRITICAL for NixOS/Real-time logging
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                bufsize=1, # Line buffered
                env=os.environ.copy() 
            )
            
            logger.info(f"Started Marker process for [bold cyan]{pdf_path.name}[/] (PID: {process.pid})")
            
            # Stream output line by line
            for line in process.stdout:
                clean_line = line.strip()
                if clean_line:
                    logger.info(f"[dim]Marker:[/] {clean_line}")
            
            # Wait for process to complete with timeout
            try:
                stdout, stderr = process.communicate(timeout=1200)
                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)
            except subprocess.TimeoutExpired:
                process.kill()
                logger.error(f"Marker timed out after 1200 seconds for {pdf_path}")
                raise

            # Marker usually creates a folder with the PDF name and a .md file inside
            md_file = self.output_dir / pdf_path.stem / f"{pdf_path.stem}.md"
            if md_file.exists():
                return md_file
            else:
                # Some versions might just put it in the output dir
                potential_md = self.output_dir / f"{pdf_path.stem}.md"
            if potential_md.exists():
                md_file = potential_md
            else:
                raise FileNotFoundError(f"Markdown file not found after processing {pdf_path}")

            # NEW: Visual Extraction Sub-system (Plan 3.2)
            self.enrich_with_visuals(md_file, self.output_dir / pdf_path.stem / "assets")
            
            return md_file

        except subprocess.CalledProcessError as e:
            logger.error(f"Marker failed for {pdf_path}: {e}")
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
