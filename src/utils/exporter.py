# src/utils/exporter.py

import json
import sqlite3
import genanki
import os
from pathlib import Path
from tqdm import tqdm
from utils.logger import setup_logger, console

logger = setup_logger("AnkiExporter")

class AnkiExporter:
    def __init__(self, db_path="study_engine.db", output_dir="output"):
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Anki Model definition
        self.model = genanki.Model(
            1607392319,
            'Atomic Flashcard Model',
            fields=[
                {'name': 'Question'},
                {'name': 'Answer'},
                {'name': 'Source'},
                {'name': 'Type'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '<div style="font-family: Arial; font-size: 20px; text-align: center; color: #333;">{{Question}}</div>',
                    'afmt': '{{FrontSide}}<hr id="answer"><div style="font-family: Arial; font-size: 18px; text-align: center;">{{Answer}}</div><br><div style="font-size: 12px; color: gray;">Source: {{Source}} | Type: {{Type}}</div>',
                },
            ])

    def export_all(self, deck_name="Study Course"):
        deck = genanki.Deck(2059400110, deck_name)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT output_json, metadata FROM processing_queue WHERE status = 'COMPLETED'")
        
        total_cards = 0
        all_metadata = []
        
        rows = cursor.fetchall()
        
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
        
        if not rows:
            logger.warning("[bold red]No completed cards found to export.[/]")
            conn.close()
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            task_id = progress.add_task("Exporting Cards", total=len(rows))
            
            for row in rows:
                cards_data = json.loads(row[0])
                metadata = json.loads(row[1])
                all_metadata.append(metadata)
                
                for card in cards_data.get("flashcards", []):
                    note = genanki.Note(
                        model=self.model,
                        fields=[
                            card.get('front', ''),
                            card.get('back', ''),
                            metadata.get('source_file', 'Unknown'),
                            card.get('type', 'concept')
                        ]
                    )
                    deck.add_note(note)
                    total_cards += 1
                
                progress.advance(task_id)
        
        conn.close()
        
        if total_cards > 0:
            output_file = self.output_dir / f"{deck_name.replace(' ', '_')}.apkg"
            genanki.Package(deck).write_to_file(output_file)
            logger.info(f"Exported [bold green]{total_cards}[/] cards to [bold cyan]{output_file}[/]")
            self.generate_report(all_metadata)
        else:
            logger.warning("[bold red]No cards found in completed chunks.[/]")

    def generate_report(self, metadata_list):
        report_path = self.output_dir / "Coverage_Report.md"
        with open(report_path, "w") as f:
            f.write("# Study Engine Coverage Report\n\n")
            f.write(f"Total Sources Processed: {len(metadata_list)}\n\n")
            f.write("## Processed Files\n")
            for meta in metadata_list:
                f.write(f"- {meta.get('source_file', 'Unknown')}\n")
        logger.info(f"Report generated at [bold cyan]{report_path}[/]")

if __name__ == "__main__":
    exporter = AnkiExporter()
    exporter.export_all()
