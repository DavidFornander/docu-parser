#!/usr/bin/env bash

echo "🚀 Starting Zero-Loss File Manager on http://localhost:8000"
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 src/web/server.py
