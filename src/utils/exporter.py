# src/utils/exporter.py

import json
import sqlite3
import csv
import os
from pathlib import Path
from utils.logger import setup_logger, console

logger = setup_logger("CSVExporter")

class CSVExporter:
    def __init__(self, db_path="study_engine.db", output_dir="output"):
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def export_all(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT output_json, metadata FROM processing_queue WHERE status = 'COMPLETED'")
        
        rows = cursor.fetchall()
        if not rows:
            logger.warning("[bold red]No completed cards found to export.[/]")
            conn.close()
            return

        # Group cards by source file
        source_groups = {}
        for row in rows:
            cards_data = json.loads(row[0])
            metadata = json.loads(row[1])
            source_file = metadata.get('source_file', 'Unknown_Source')
            if source_file not in source_groups:
                source_groups[source_file] = []
            source_groups[source_file].extend(cards_data.get("flashcards", []))

        total_cards = 0
        
        # 1. Export individual CSVs
        for source_file, cards in source_groups.items():
            stem = Path(source_file).stem
            output_file = self.output_dir / f"{stem}_cards.csv"
            
            with open(output_file, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Question", "Answer", "Source", "Type"])
                for card in cards:
                    writer.writerow([
                        card.get('front', ''),
                        card.get('back', ''),
                        source_file,
                        card.get('type', 'concept')
                    ])
                    total_cards += 1
            logger.info(f"Exported [bold green]{len(cards)}[/] cards to [bold cyan]{output_file}[/]")

        # 2. Export Master CSV
        master_file = self.output_dir / "master_study_cards.csv"
        with open(master_file, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Answer", "Source", "Type"])
            for source_file, cards in source_groups.items():
                for card in cards:
                    writer.writerow([
                        card.get('front', ''),
                        card.get('back', ''),
                        source_file,
                        card.get('type', 'concept')
                    ])
        
        conn.close()
        logger.info(f"Master export complete: [bold cyan]{master_file}[/]")
        self.generate_report([{"source_file": s} for s in source_groups.keys()])

    def generate_report(self, metadata_list):
        report_path = self.output_dir / "Coverage_Report.md"
        with open(report_path, "w") as f:
            f.write("# Study Engine Coverage Report\n\n")
            f.write(f"Total Sources Processed: {len(metadata_list)}\n\n")
            f.write("## Processed Files\n")
            # Deduplicate filenames
            unique_files = sorted(list(set(meta.get('source_file', 'Unknown') for meta in metadata_list)))
            for filename in unique_files:
                f.write(f"- {filename}\n")
        logger.info(f"Report generated at [bold cyan]{report_path}[/]")

if __name__ == "__main__":
    exporter = CSVExporter()
    exporter.export_all()
