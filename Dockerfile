FROM python:3.14 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.3.1 && \
    poetry config virtualenvs.in-project true

COPY pyproject.toml poetry.lock ./
RUN poetry install

FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /app/.venv .venv/
COPY . .

CMD ["/app/.venv/bin/gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
