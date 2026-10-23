FROM python:3.11-slim-bookworm

# Avoid interactive prompts during package installation and enforce UTF-8 locale
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=5800 \
    HOST=0.0.0.0 \
    STORAGE_DIR=/storage \
    CONFIG_DIR=/config \
    MKVMERGE_PATH=mkvmerge \
    MKVPROPEDIT_PATH=mkvpropedit

# Install system dependencies, mkvtoolnix, gosu and ca-certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    mkvtoolnix \
    gosu \
    ca-certificates \
    tzdata \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python requirements
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy source code and entrypoint
COPY backend /app/backend
COPY frontend /app/frontend
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create persistent mount points
RUN mkdir -p /storage /config

# Expose Web port
EXPOSE 5800

# Mountable directories
VOLUME ["/storage", "/config"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5800/ || exit 1

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["python", "/app/backend/run.py"]
