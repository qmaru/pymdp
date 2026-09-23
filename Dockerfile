ARG PYTHON_VERSION=3.13

FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-trixie-slim AS builder

WORKDIR /src

COPY README.md pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-editable --no-install-project

COPY src/ ./src/

RUN uv sync --frozen --no-dev --no-editable

FROM gcr.io/distroless/python3-debian13

ARG PYTHON_VERSION

LABEL description="get mdpr image urls"

COPY --from=builder /src/.venv /venv

ENV PYTHONPATH=/venv/lib/python${PYTHON_VERSION}/site-packages \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENTRYPOINT ["/usr/bin/python3.13", "/venv/bin/mdpdl"]
