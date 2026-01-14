#!/usr/bin/env bash
set -e

# Define the Nix command wrapper
# This ensures all Python scripts run inside the correct Nix environment with GPU libraries
NIX_CMD="nix develop --command bash -c"
ENV_SETUP="export LD_LIBRARY_PATH=\$NIX_LD_LIBRARY_PATH:/run/opengl-driver/lib && source .venv/bin/activate && export PYTHONPATH=\$PYTHONPATH:\$(pwd)/src"

echo "🚀 Starting Zero-Loss Learning Engine Pipeline..."

# 1. Initialize Database
if [ ! -f "study_engine.db" ]; then
    echo "📦 Initializing Database..."
    $NIX_CMD "$ENV_SETUP && python src/db/init_db.py"
else
    echo "✅ Database already exists."
fi

# 2. Ingestion (PDF -> Markdown -> Chunks -> DB)
echo "📄 Phase 1: Ingestion..."
$NIX_CMD "$ENV_SETUP && python src/main.py"

# 3. Processing (Inference & Verification)
echo "🧠 Phase 2: Processing (Worker)..."
echo "   (This may take time depending on your GPU)"
$NIX_CMD "$ENV_SETUP && python src/worker.py"

# 4. Export (DB -> Anki)
echo "📤 Phase 3: Exporting..."
$NIX_CMD "$ENV_SETUP && python src/utils/exporter.py"

echo "🎉 Pipeline Complete! Check 'output/' for your Anki deck."
