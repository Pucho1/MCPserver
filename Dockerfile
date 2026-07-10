# =========================
# Stage 1: Builder
# =========================

FROM python:3.13-slim-bookworm AS builder

WORKDIR /build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock README.md ./

COPY server.py ./
COPY config ./config
COPY core ./core
COPY middleware ./middleware
COPY prompts ./prompts
COPY resources ./resources
COPY schemas ./schemas
COPY services ./services
COPY tools ./tools


# Construye nuestro artefacto Python
RUN uv build --wheel

# Exporta las dependencias runtime exactas desde uv.lock
RUN uv export \
    --locked \
    --no-dev \
    --no-emit-project \
    --format requirements.txt \
    --output-file requirements.txt

# =========================
# Stage 2: Runtime
# =========================

FROM python:3.13-slim-bookworm AS runtime

WORKDIR /app

# Copiamos los artefactos de construcción desde el stage builder
COPY --from=builder /build/requirements.txt .

COPY --from=builder /build/dist/*.whl .

# instalamos primero el entorno exacto:
RUN pip install --no-cache-dir -r requirements.txt

# Luego instalamos nuestro artefacto Python
RUN pip install --no-cache-dir --no-deps ./*.whl


RUN groupadd --system appgroup \
    && useradd --system --gid appgroup --home-dir /app appuser \
    && mkdir -p /data \
    && chown -R appuser:appgroup /data

USER appuser

CMD ["mcp-server"]