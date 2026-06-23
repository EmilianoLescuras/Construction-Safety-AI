# syntax=docker/dockerfile:1.7
#
# Worker container: full inference pipeline (detect + track + rules) that
# POSTs events to the API. Heavy image (torch + opencv + ultralytics).
# Run on a host with the source video + access to the API URL.
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# OpenCV runtime libs (libGL for cv2.imshow / video codecs).
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 ffmpeg \
 && rm -rf /var/lib/apt/lists/*

COPY requirements-worker.txt ./
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-worker.txt

COPY src ./src
COPY config ./config
COPY models ./models

RUN useradd --create-home --shell /bin/bash worker \
 && mkdir -p outputs \
 && chown -R worker:worker /app
USER worker

# Default: print help. Override at run-time with the actual job.
ENTRYPOINT ["python", "-m", "src.worker.cli"]
CMD ["--help"]
