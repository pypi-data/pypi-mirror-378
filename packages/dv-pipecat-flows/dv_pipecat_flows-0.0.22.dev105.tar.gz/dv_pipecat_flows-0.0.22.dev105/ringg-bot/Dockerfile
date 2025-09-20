# Local development Dockerfile - uses custom pipecat build
FROM python:3.12-bullseye

# Install system dependencies including build tools for pyrnnoise
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    cmake \
    build-essential \
    ffmpeg \
    curl \
    ca-certificates \
    && git lfs install \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the entire project directory
COPY . /app/

# Install pipecat from local build with all required extras
RUN set -eux && \
    WHEEL=$(ls -1t /app/pipecat_dist/*.whl | head -1) && \
    if [ -z "$WHEEL" ]; then \
        echo "Error: No wheel file found in /app/pipecat_dist/. Exiting."; \
        exit 1; \
    fi && \
    echo "Installing local pipecat wheel: $WHEEL" && \
    pip install --no-cache-dir \
    "${WHEEL}[daily,cartesia,openai,silero,deepgram,azure,elevenlabs,noisereduce,gladia,google,groq,sentry,soundfile,local-smart-turn,speechmatics,remote-smart-turn,anthropic]"

# Set working directory to the ringg-bot directory
WORKDIR /app/ringg-bot

# Install Python dependencies for pyrnnoise
RUN pip install --no-cache-dir numpy cython

# Build and install pyrnnoise
RUN git clone --recursive https://github.com/pengzhendong/pyrnnoise.git /tmp/pyrnnoise && \
    cd /tmp/pyrnnoise && \
    git submodule update --init --recursive && \
    cmake -B build -DCMAKE_BUILD_TYPE=Release && \
    cmake --build build --target install && \
    pip install . && \
    rm -rf /tmp/pyrnnoise

# Install application requirements 
RUN pip install --no-cache-dir -r requirements.txt

# Set PYTHONPATH to include the project root so pipecat_flows can be imported
ENV PYTHONPATH=/app/src:$PYTHONPATH


EXPOSE 8765
CMD ["python", "server.py"]