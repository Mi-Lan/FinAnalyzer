FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy application code
COPY . .

# Install data-adapter as a local package
RUN pip install -e /data-adapter

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"] 