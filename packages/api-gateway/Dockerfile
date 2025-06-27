FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy api-gateway poetry files
COPY packages/api-gateway/pyproject.toml packages/api-gateway/poetry.lock* ./

# Install dependencies without installing the project itself
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Copy api-gateway code
COPY packages/api-gateway/src ./src

# Copy data-adapter package
COPY packages/data-adapter /data-adapter

# Install data-adapter
RUN cd /data-adapter && pip install -e .

# Set PYTHONPATH to include src directory
ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"] 