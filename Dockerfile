FROM python:3.14-slim AS builder

WORKDIR /build
COPY pyproject.toml README.md ./
COPY app ./app
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/app/data/taskflow.db

RUN addgroup --system taskflow && adduser --system --ingroup taskflow taskflow
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --chown=taskflow:taskflow app ./app
RUN mkdir -p /app/data && chown taskflow:taskflow /app/data

USER taskflow
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
