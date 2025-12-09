# 1. Base Image
FROM python:3.11-slim

# 2. Set Environment Variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures Python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED 1
# Tell Poetry to not create a new virtual env
ENV POETRY_VIRTUALENVS_CREATE=false

# 3. Install Poetry
RUN pip install poetry

# 4. Set Working Directory
WORKDIR /app

# 5. Copy dependency definitions and install
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction --no-ansi

# 6. Copy application code
COPY ./app ./app

# 7. Expose port and set command
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
