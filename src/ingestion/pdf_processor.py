import os
import subprocess
import logging
from pathlib import Path
from utils.logger import setup_logger
from inference.vision import ImageDescriber
from docling.document_converter import DocumentConverter

logger = setup_logger("PDFProcessor")

class PDFProcessor:
    def __init__(self, input_dir="input", output_dir="output", assets_dir="assets"):
        self.input_dir = Path(input_dir)
        
        # Notebook Override
        target_notebook = os.environ.get("TARGET_NOTEBOOK")
        if target_notebook:
            self.output_dir = Path(output_dir) / target_notebook
            logger.info(f"Targeting notebook output: {self.output_dir}")
        else:
            self.output_dir = Path(output_dir)
        
        self.assets_dir = Path(assets_dir)
        
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        self.converter = DocumentConverter()

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
            for i, img_path in enumerate(image_files):
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
        Converts a single PDF to Markdown using Docling.
        """
        pdf_path = Path(pdf_path)
        output_subfolder = self.output_dir / pdf_path.stem
        output_subfolder.mkdir(exist_ok=True)
        
        md_file = output_subfolder / f"{pdf_path.stem}.md"
        if md_file.exists():
            logger.info(f"Markdown already exists for {pdf_path}, skipping conversion.")
            return md_file

        logger.info(f"Processing PDF with Docling: {pdf_path}")
        
        # Ensure assets folder exists for visual enrichment
        assets_folder = output_subfolder / "assets"
        assets_folder.mkdir(exist_ok=True)
        
        try:
            # Convert the document
            result = self.converter.convert(str(pdf_path))
            markdown_content = result.document.export_to_markdown()
            
            # Save to file
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            logger.info(f"Docling conversion successful: {md_file}")

            # NEW: Visual Extraction Sub-system (Plan 3.2)
            # Docling might extract images too, but for now we'll keep the existing structure
            self.enrich_with_visuals(md_file, self.output_dir / pdf_path.stem / "assets")
            
            return md_file

        except Exception as e:
            logger.error(f"Docling failed for {pdf_path}: {e}")
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
