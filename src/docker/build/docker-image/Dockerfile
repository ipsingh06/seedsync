# SeedSync Docker Image - Optimized Build
# Target size: <200MB (down from 439MB)

# ==============================================================================
# Stage 1: Build Angular Frontend
# ==============================================================================
FROM node:20-bookworm-slim AS angular-builder

WORKDIR /app
COPY src/angular/package*.json ./
RUN npm install --include=dev
COPY src/angular/ ./
RUN ./node_modules/.bin/ng build --configuration production --output-path /build/html

# ==============================================================================
# Stage 2: Build scanfs binary with PyInstaller
# ==============================================================================
FROM python:3.12-slim-bookworm AS scanfs-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pyinstaller

COPY src/python/scan_fs.py /src/
COPY src/python/system/ /src/system/

WORKDIR /build
RUN pyinstaller /src/scan_fs.py \
    --onefile \
    -p /src \
    --distpath /build/dist \
    --workpath /build/work \
    --specpath /build \
    --name scanfs \
    && strip /build/dist/scanfs 2>/dev/null || true

# ==============================================================================
# Stage 3: Final Runtime Image (Optimized)
# ==============================================================================
FROM python:3.12-slim-bookworm AS runtime

LABEL maintainer="nitrobass24" \
      description="SeedSync - Seedbox file synchronization tool" \
      version="0.9.0"

# Install only essential runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    lftp \
    openssh-client \
    p7zip \
    p7zip-full \
    unrar-free \
    gosu \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set up RAR codec symlink
RUN ln -sf /usr/lib/p7zip/Codecs/Rar.so /usr/lib/p7zip/Codecs/Rar29.so 2>/dev/null || true

# Set locale
ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create directory structure
RUN mkdir -p /app/python /app/html /config /downloads

# Install Python dependencies directly with pip (no Poetry overhead)
COPY src/python/requirements.txt /app/python/
RUN pip install --no-cache-dir -r /app/python/requirements.txt \
    && rm -rf /root/.cache/pip

# Copy application source
COPY src/python/ /app/python/

# Copy built artifacts from previous stages
# Angular 17+ outputs to browser/ subfolder
COPY --from=angular-builder /build/html/browser /app/html
COPY --from=scanfs-builder /build/dist/scanfs /app/scanfs

# Copy and set up entrypoint
COPY src/docker/build/docker-image/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh /app/scanfs

# Runtime configuration
ENV PUID=1000 \
    PGID=1000

EXPOSE 8800
VOLUME ["/config", "/downloads"]

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python", "/app/python/seedsync.py", "-c", "/config", "--html", "/app/html", "--scanfs", "/app/scanfs"]
