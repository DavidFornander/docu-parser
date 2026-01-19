# Zero-Loss Learning Engine

An autonomous, local-first AI pipeline designed to achieve 100% information coverage from courseware. Unlike standard RAG systems that summarize, this engine uses **Atomic Extraction** and a **Reverse RAG Audit** to ensure no detail is lost.

## 🚀 The "Zero-Loss" Philosophy
Summarization is lossy. In high-stakes learning (medical, engineering, law), omission is failure. This engine:
1. **Decomposes** text into atomic Question-Answer pairs.
2. **Sees Diagrams**: Uses VLMs to describe charts, labels, and arrows, injecting them as text context.
3. **Audits Coverage**: Reconstructs the source text from generated cards to find gaps.
4. **Verifies Factuality**: Uses NLI (Cross-Encoders) to ensure every flashcard is strictly supported by the source material.
5. **Repairs Gaps**: Automatically triggers a "Chain of Verification" loop for missing info.

## 🛠 Tech Stack
- **Inference**: [vLLM](https://github.com/vllm-project/vllm) for high-throughput local LLM execution.
- **Parsing**: [Docling](https://github.com/DS4SD/docling) for advanced PDF to Markdown conversion.
- **State**: SQLite-based queue for crash-resilient processing.
- **UI**: FastAPI + Tailwind Manager with real-time VRAM monitoring and live logs.

## 🏃 Usage & Scripts

### Primary Entry Point: Web UI
The recommended way to use the engine is via the Web Manager:
```bash
./start_ui.sh
```
*   **Purpose:** Manages notebooks, uploads, pipeline execution, and monitoring.
*   **Access:** `http://localhost:8000`
*   **Behavior:** Runs the server in a `tmux` session named `ui` for persistence.

### CLI Entry Point: Automated Pipeline
If you want to process everything in one shot via terminal:
```bash
./run.sh
```
*   **Purpose:** Sequentially runs Ingestion -> Worker -> Export for all notebooks.
*   **Usage:** Best for headless servers or automation.

### Developer Tool: Sandbox Environment
For developers using Podman/Docker:
```bash
./enter_sandbox.sh
```
*   **Purpose:** Builds and enters a GPU-enabled container environment.
*   **Features:** Handles NVIDIA GPU passthrough and permission mapping.

## 🏃 Manual CLI Flow (Deep Dive)
If you need granular control, you can run individual stages:

### Phase 1: Ingestion
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 src/ingestor.py
```
*Note: Set `TARGET_NOTEBOOK` env var to process a specific subfolder in `data/input`.*

### Phase 2: Processing (The Worker)
```bash
python3 src/worker.py
```

### Phase 3: Export
```bash
python3 src/utils/exporter.py
```

## ⚙️ Configuration (Variables)
All settings use the `ZERO_` prefix.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `ZERO_DATA_DIR` | Root folder for all user content | `./data` |
| `ZERO_MODEL_NAME` | HuggingFace ID or local path | `casperhansen/llama-3-8b-instruct-awq` |
| `ZERO_DEBUG` | Enable verbose logging | `false` |

## 📁 Directory Structure
- `data/`: **The "Source of Truth"**. Contains all your PDFs, database, and outputs.
  - `input/`: Your organized Notebook folders.
  - `output/`: Generated CSV decks and coverage reports.
  - `zeroloss.db`: The persistent knowledge state.
- `src/`: **The Core Logic**. Pure, stateless code modules.
- `logs/`: Process output logs.

## ⚖️ License
MIT
