#!/usr/bin/env bash

# start_service.sh
# This script enters the Nix development environment and launches the 
# Zero-Loss Engine Dashboard.

echo "🚀 Starting Zero-Loss Engine Dashboard..."

# We use nix develop --command to execute the server inside the patched environment.
# We explicitly set the PYTHONPATH so that local imports work.
nix develop --command bash -c "export PYTHONPATH=\$PYTHONPATH:\$(pwd)/src && python src/web/app.py"
