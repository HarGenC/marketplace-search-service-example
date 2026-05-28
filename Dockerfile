FROM python:3.13-slim-bookworm

RUN addgroup --system --gid 1001 appgroup
RUN adduser --system --uid 1001 --ingroup appgroup appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_DEV=1 \
    UV_FROZEN=1 \
    PYTHONPATH=/app \
    PATH="/root/.local/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv

WORKDIR /app

COPY --chown=appuser:appgroup pyproject.toml uv.lock ./
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN uv venv /app/.venv
RUN uv sync --frozen --python /app/.venv/bin/python
ENV PATH="/app/.venv/bin:$PATH"

COPY . .

RUN chown -R appuser:appgroup /app


EXPOSE 8000

USER appuser

CMD ["/entrypoint.sh"]
