# Zero-Loss Learning Engine (docu-parser)

An autonomous, local-first AI pipeline designed to achieve 100% information coverage from courseware. Unlike standard RAG systems that summarize, this engine uses **Atomic Extraction** and a **Reverse RAG Audit** to ensure no detail is lost.

## 🚀 The "Zero-Loss" Philosophy
Summarization is lossy. In high-stakes learning (medical, engineering, law), omission is failure. This engine:
1. **Decomposes** text into atomic Question-Answer pairs.
2. **Audits** coverage by attempting to reconstruct the source text from the generated cards.
3. **Repairs** gaps automatically via a "Chain of Verification" loop.

## 🛠 Architecture
- **Inference**: [vLLM](https://github.com/vllm-project/vllm) for high-throughput local LLM execution.
- **Parsing**: [Marker](https://github.com/vikas-kumar/marker-pdf) for deep-learning-based PDF to Markdown conversion.
- **State**: SQLite-based job queue for persistent, crash-resilient processing.
- **Verification**: Sentence-Transformers for semantic coverage auditing.
- **Export**: Anki-compatible `.apkg` generation.

## 📦 Prerequisites (NixOS Setup)
This project is optimized for NixOS using **Distrobox** to manage complex GPU/Python dependencies.

1. **Enter the environment**:
   ```bash
   distrobox enter ai-lab
   ```
2. **Dependencies**:
   Inside the container, ensure the following are installed:
   ```bash
   pip install vllm marker-pdf sentence-transformers genanki torch
   ```

## 🏃 Usage Flow

### 1. Ingestion (Phase 1)
Place your PDFs in the `input/` folder.
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 src/main.py
```
This converts PDFs to Markdown, performs semantic chunking, and populates the SQLite queue.

### 2. Processing (Phase 2 & 3)
Run the worker to generate and verify flashcards.
```bash
python3 src/worker.py
```
*Note: Uses `casperhansen/llama-3-8b-instruct-awq` by default for 12GB VRAM compatibility.*

### 3. Export
Generate your Anki deck.
```bash
python3 src/utils/exporter.py
```

## 📁 Directory Structure
- `input/`: Raw PDFs.
- `output/`: Processed Markdown and Anki decks.
- `assets/`: Extracted diagrams and images.
- `src/`:
  - `ingestion/`: PDF processing & chunking.
  - `inference/`: vLLM interaction & prompt engineering.
  - `verification/`: Semantic coverage audit.
  - `db/`: SQLite job queue management.

## ⚖️ License
MIT
