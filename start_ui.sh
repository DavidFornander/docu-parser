#!/usr/bin/env bash

SESSION_NAME="ui"

# Check if the session already exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "⚠️  UI is already running in tmux session '$SESSION_NAME'."
    echo "👉 Use 'tmux attach -t $SESSION_NAME' to view logs or 'tmux kill-session -t $SESSION_NAME' to stop it."
    exit 0
fi

echo "🚀 Starting Zero-Loss File Manager on http://localhost:8000"
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# If not in tmux, start a detached session. If in tmux, run in foreground.
if [ -z "$TMUX" ]; then
    tmux new-session -d -s "$SESSION_NAME" "export PYTHONPATH=$PYTHONPATH:$(pwd)/src && python3 src/web/server.py"
    echo "✅ UI started in background tmux session '$SESSION_NAME'."
    echo "👉 Use 'tmux attach -t $SESSION_NAME' to view live logs."
else
    python3 src/web/server.py
fi
