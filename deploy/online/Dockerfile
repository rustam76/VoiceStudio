# syntax=docker/dockerfile:1
FROM oven/bun:1.4.2-alpine AS web
WORKDIR /app
COPY package.json bun.lock ./
COPY frontend/package.json frontend/package.json
RUN bun install --frozen-lockfile --ignore-scripts
COPY config config
COPY frontend/src frontend/src
COPY frontend/public frontend/public
COPY frontend/tests frontend/tests
COPY frontend/vite.web.config.ts frontend/vite.web.config.ts
RUN bun run build:web

FROM ghcr.io/astral-sh/uv:0.12.5 AS uv
FROM python:3.12-slim-bookworm AS runtime
COPY --from=uv /uv /usr/local/bin/uv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend PATH=/app/.venv/bin:$PATH \
    OMNIVOICE_SERVER_MODE=1 OMNIVOICE_STUDIO_LITE=1 OMNIVOICE_MCP_DISABLE=1 \
    OMNIVOICE_TTS_BACKEND=supertonic3 \
    OMNIVOICE_DATA_DIR=/data HF_HOME=/data/huggingface \
    OMNIVOICE_PRELOAD_CAPTURE_ASR=0 OMNIVOICE_PRELOAD_WATERMARK=0 \
    SUPERTONIC_INTRA_OP_THREADS=2 SUPERTONIC_INTER_OP_THREADS=1 \
    OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
    OMNIVOICE_GPU_WORKERS=1 OMNIVOICE_CPU_POOL=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 ffmpeg libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 studio \
    && mkdir -p /data && chown studio:studio /data
WORKDIR /app
COPY deploy/online/pyproject.toml deploy/online/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_LINK_MODE=copy uv sync --frozen --no-default-groups --no-install-project \
    && .venv/bin/python -c "import torch, supertonic; assert torch.version.cuda is None"
COPY LICENSE LICENSE-NOTICE.md README.md ./
COPY backend backend
COPY omnivoice omnivoice
COPY config config
COPY alembic.ini package.json ./
COPY scripts/online-model.py scripts/online-model.py
COPY --from=web /app/frontend/dist frontend/dist
USER studio
EXPOSE 3900
VOLUME ["/data"]
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=5 \
    CMD ["python", "backend/docker_entrypoint.py", "--health-check"]
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "3900", "--workers", "1", "--no-access-log"]
