# Zero-Loss Learning Engine (docu-parser)

An autonomous, local-first AI pipeline designed to achieve 100% information coverage from courseware. Unlike standard RAG systems that summarize, this engine uses **Atomic Extraction** and a **Reverse RAG Audit** to ensure no detail is lost.

## 🚀 The "Zero-Loss" Philosophy
Summarization is lossy. In high-stakes learning (medical, engineering, law), omission is failure. This engine:
1. **Decomposes** text into atomic Question-Answer pairs.
2. **Sees Diagrams**: Uses a Vision Language Model (VLM) to describe charts, labels, and arrows, injecting them as text context.
3. **Audits** coverage by attempting to reconstruct the source text from the generated cards.
4. **Verifies Factuality**: Uses a Cross-Encoder (NLI) to ensure every flashcard is strictly supported by the source material.
5. **Repairs** gaps automatically via a "Chain of Verification" loop.

## 🛠 Architecture
- **Inference**: [vLLM](https://github.com/vllm-project/vllm) for high-throughput local LLM execution (Llama-3-8B).
- **Vision**: [Moondream2](https://github.com/vikhyat/moondream) for lightweight diagram analysis.
- **Parsing**: [Marker](https://github.com/vikas-kumar/marker-pdf) for deep-learning-based PDF to Markdown conversion.
- **State**: SQLite-based job queue for persistent, crash-resilient processing.
- **Verification**: Sentence-Transformers for semantic coverage auditing and Cross-Encoders for fact-checking.
- **Export**: Anki-compatible `.apkg` generation.

## 📦 Environment Setup (NixOS)
This project is optimized for NixOS using **Nix Flakes** to provide a patched environment where standard Python AI wheels can run natively.

1. **Enter the Development Shell**:
   ```bash
   nix develop
   ```
   *This automatically creates/activates a `.venv` and patches library paths.*

2. **Install Dependencies** (First time only):
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 Usage Flow

### Quick Start (Recommended)
We provide a unified script to run the entire pipeline (Ingestion -> Processing -> Export):

```bash
chmod +x run.sh
./run.sh
```

### Manual Execution

#### 1. Ingestion (Phase 1)
Place your PDFs in the `input/` folder.
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 src/main.py
```
This converts PDFs to Markdown, performs semantic chunking, and populates the SQLite queue.

#### 2. Processing (Phase 2 & 3)
Run the worker to generate and verify flashcards.
```bash
python3 src/worker.py
```
*Note: Uses `Qwen/Qwen2.5-0.5B-Instruct` by default for high speed and low VRAM usage.*

#### 3. Export
Generate your Anki deck.
```bash
python3 src/utils/exporter.py
```

## 📊 Monitoring
The system logs its exact state every 5 seconds to:
- **Terminal**: Direct log output.
- **File**: `logs/system_state.jsonl` (Structured heartbeat).

To monitor the background heartbeat:
```bash
tail -f logs/system_state.jsonl
```

## 📁 Directory Structure
- `input/`: Raw PDFs.
- `output/`: Processed Markdown and Anki decks.
- `assets/`: Extracted diagrams and images.
- `logs/`: Heartbeat and system state logs.
- `src/`:
  - `ingestion/`: PDF processing & chunking.
  - `inference/`: vLLM interaction & prompt engineering.
  - `verification/`: Semantic coverage audit.
  - `db/`: SQLite job queue management.

## ⚖️ License
MIT