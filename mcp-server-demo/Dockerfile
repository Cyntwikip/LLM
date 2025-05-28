# # Use Python 3.11 base image
# FROM python:3.11-slim

# # Set working directory
# WORKDIR /app

# # Install uv (fast Python package manager)
# RUN pip install --upgrade pip && pip install uv

# # Copy lockfile and pyproject.toml first for better Docker cache
# COPY uv.lock pyproject.toml /app
# # COPY . /app

# # RUN uv pip compile
# RUN ls

# # Install dependencies using uv
# # RUN uv pip sync
# RUN uv sync
# # RUN uv pip install -r pyproject.toml

# # Copy the rest of the application code
# COPY . /app

# # Expose the port your server will run on
# EXPOSE 8081

# # Run the server
# CMD ["python", "server_rag.py"]

FROM python:3.11-slim-bookworm AS base
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.4.9 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY uv.lock pyproject.toml /app

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev
# FROM base
# COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8081
EXPOSE 8501

# CMD ["python", "server_rag.py", "--server.port=8081", "--server.address=0.0.0.0"]

# CMD ["streamlit", "run", "app.py", "--server.port=8600", "--server.address=0.0.0.0"]
# CMD ["streamlit", "run", "rag_chat_app_v2.py", "--server.port=8501", "--server.address=0.0.0.0"]