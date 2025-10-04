ARG BASE_IMAGE=python:3.12.0-slim-bullseye
FROM $BASE_IMAGE

# Use the uv binary
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /bin/uv

# Allows the container to start up faster.
ENV UV_COMPILE_BYTECODE=1

# Set working directory as `/code/`
WORKDIR /code

# Copy project packages & dependcies
COPY pyproject.toml /code/pyproject.toml
COPY uv.lock /code/uv.lock
COPY .python-version /code/.python-version

# Install uv via pip, then install all packages.
# https://docs.astral.sh/uv/reference/cli/#uv-sync
RUN pip install --no-cache-dir --upgrade pip==25.2 && \
    uv sync --locked

# Copy application code to `/code/app/`
COPY .chainlit /code/.chainlit
COPY app.py config.py inference_models.py  tools.py /code/app/

# Start ..chainlit application
# https://docs.chainlit.io/backend/command-line
CMD ["uv", "run", "chainlit", "run", "--host", "0.0.0.0", "--port", "8000", "/code/app/app.py"]
