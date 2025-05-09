FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./

ENV UV_COMPILE_BYTECODE=1 \
    UV_FROZEN=1 \
    UV_LINK_MODE=copy \
    UV_NO_INSTALLER_METADATA=1 \
    VIRTUAL_ENV=/app/.venv

ARG LOCAL=false

RUN --mount=type=cache,target=/root/.cache/uv \
    if [ "$LOCAL" = "true" ]; then EXTRA_ARGS="--extra local"; fi; \
    uv sync --no-install-project --no-dev $EXTRA_ARGS

ENV PATH="/app/.venv/bin:$PATH"

COPY backend/ ./backend

ENV PYTHONUNBUFFERED=1
ENV LOCAL=${LOCAL}

EXPOSE 8000
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

CMD ["fastapi", "run", "backend/app.py", "--host", "0.0.0.0", "--port", "8000"]
