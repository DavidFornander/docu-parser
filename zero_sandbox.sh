#!/usr/bin/env bash

IMAGE_NAME="docu-parser-sandbox"
CONTAINER_NAME="docu-parser-agent"

# Always run build - Podman will use cache if nothing has changed
echo "🔨 Syncing Sandboxed Environment..."
podman build --build-arg USER_ID=$(id -u) -t $IMAGE_NAME .

echo "🚀 Entering Sandboxed Environment (GPU Enabled)..."

# --device nvidia.com/gpu=all: Passes all NVIDIA GPUs to the container
# --security-opt label=disable: Allows volume access on SELinux/NixOS systems
# --userns=keep-id: Ensures file permissions match your host user
# -p 8000-8001:8000-8001: Maps host ports to container ports for dashboards
podman run -it --rm \
  --name $CONTAINER_NAME \
  --device nvidia.com/gpu=all \
  --security-opt label=disable \
  --userns=keep-id \
  -p 8000:8000 \
  -p 8001:8001 \
  -v "$(pwd):/workspace:Z" \
  -e "GEMINI_API_KEY=$GEMINI_API_KEY" \
  -e "PYTHONPATH=/workspace/src" \
  $IMAGE_NAME
