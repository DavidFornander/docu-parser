#!/usr/bin/env bash
set -e

# Setup Python Path
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

echo "🚀 Starting Zero-Loss Learning Engine Pipeline..."

# 1. Initialize Database
if [ ! -f "study_engine.db" ]; then
    echo "📦 Initializing Database..."
    python3 src/db/init_db.py
else
    echo "✅ Database already exists."
fi

# 2. Ingestion (PDF -> Markdown -> Chunks -> DB)
echo "📄 Phase 1: Ingestion..."
python3 src/ingestor.py

# 3. Processing (Inference & Verification)
echo "🧠 Phase 2: Processing (Worker)..."
echo "   (This may take time depending on your GPU)"
python3 src/worker.py

# 4. Export (DB -> CSV)
echo "📤 Phase 3: Exporting..."
python3 src/utils/exporter.py

echo "🎉 Pipeline Complete! Check 'output/' for your CSV files."