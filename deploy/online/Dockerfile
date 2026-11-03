# syntax=docker/dockerfile:1
FROM oven/bun:1.4.2-alpine AS web
WORKDIR /app
COPY package.json bun.lock ./
COPY electron/package.json electron/package.json
RUN bun install --frozen-lockfile --ignore-scripts
COPY config config
COPY electron/src/renderer electron/src/renderer
COPY electron/src/shared electron/src/shared
COPY electron/public electron/public
COPY electron/tests electron/tests
COPY electron/vite.web.config.ts electron/vite.web.config.ts
ENV VOICESTUDIO_ONLINE_BUILD=1
RUN bun run build:web

FROM ghcr.io/astral-sh/uv:0.12.5 AS uv
FROM python:3.12-slim-bookworm AS runtime
COPY --from=uv /uv /usr/local/bin/uv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend PATH=/opt/runtime/.venv/bin:$PATH \
    OMNIVOICE_ONLINE=1 OMNIVOICE_SERVER_MODE=1 OMNIVOICE_TTS_BACKEND=supertonic3 \
    OMNIVOICE_DATA_DIR=/data HF_HOME=/data/huggingface \
    SUPERTONIC_INTRA_OP_THREADS=2 SUPERTONIC_INTER_OP_THREADS=1 \
    OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
    OMNIVOICE_GPU_WORKERS=1 OMNIVOICE_CPU_POOL=1
RUN apt-get update && apt-get install -y --no-install-recommends libsndfile1 ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 studio \
    && mkdir -p /data && chown studio:studio /data
WORKDIR /opt/runtime
COPY deploy/online/pyproject.toml deploy/online/uv.lock ./
RUN uv sync --frozen --no-dev --no-cache \
    && .venv/bin/python -c "import torch; assert torch.version.cuda is None; import supertonic"
WORKDIR /app
COPY backend backend
COPY omnivoice/__init__.py omnivoice/__init__.py
COPY omnivoice/utils omnivoice/utils
COPY config config
COPY alembic.ini package.json LICENSE LICENSE-NOTICE.md ./
COPY scripts/online-model.py scripts/online-model.py
COPY --from=web /app/frontend/dist frontend/dist
USER studio
EXPOSE 3900
VOLUME ["/data"]
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3900/health', timeout=4)"
CMD ["python", "-m", "uvicorn", "online:app", "--host", "0.0.0.0", "--port", "3900", "--workers", "1", "--no-access-log", "--no-proxy-headers"]
