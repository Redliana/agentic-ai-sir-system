FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-workflow.txt /tmp/requirements-workflow.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements-workflow.txt

COPY src /app/src
COPY configs /app/configs
COPY scripts /app/scripts
COPY README.md /app/README.md

ENV PYTHONPATH=/app/src

CMD ["bash"]
