# Base image
FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/tmp/poetry_cache'

# Set work directory
WORKDIR /app

# 1. Iranian debian mirrors (runflare)
RUN sed -i 's/deb.debian.org/mirror-linux.runflare.com/g' /etc/apt/sources.list.d/debian.sources || \
    (echo "deb http://mirror-linux.runflare.com/debian bookworm main" > /etc/apt/sources.list && \
     echo "deb http://mirror-linux.runflare.com/debian-security bookworm-security main" >> /etc/apt/sources.list)

# 2. Install system dependencies
# Added libssl-dev for cryptography and libpq-dev for postgres/psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Install poetry (matching pyproject.toml requirement)
RUN pip install --no-cache-dir "poetry>=2.0.0"

# 4. Copy configuration files
COPY pyproject.toml poetry.lock* /app/

# 5. Install dependencies
# We use --no-root because the app code isn't copied yet (better caching)
RUN poetry install --only main --no-root && rm -rf $POETRY_CACHE_DIR

# 6. Copy project files
COPY . /app/

# 7. Expose the port
EXPOSE 8000

# 8. Command to run the application
# Changed host to 0.0.0.0 for external access
CMD ["uvicorn", "config:app", "--host", "0.0.0.0", "--port", "8000"]