# Use NVIDIA CUDA base for GPU support
FROM nvidia/cuda:12.3.1-runtime-ubuntu22.04

# Prevent interactive prompts during install
ENV DEBIAN_FRONTEND=noninteractive

# Install core dev tools and libraries for PDF/Image processing
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    sudo \
    libgl1 \
    libglib2.0-0 \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Set up a non-root user that matches host UID (typical default is 1000)
ARG USER_ID=1000
RUN useradd -m -u ${USER_ID} -s /bin/bash developer && \
    echo "developer ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER root
# Ensure a modern Node.js version for the Gemini CLI
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @google/gemini-cli

USER developer
WORKDIR /workspace

# Ensure local bin is in PATH
ENV PATH="/home/developer/.local/bin:${PATH}"

# Install the Google Generative AI SDK (for library use) 
# and the project's own requirements
COPY requirements.txt .
RUN pip3 install --user --upgrade pip setuptools \
    && pip3 install --user google-generativeai \
    && pip3 install --user -r requirements.txt

# Default command
CMD ["/bin/bash"]
