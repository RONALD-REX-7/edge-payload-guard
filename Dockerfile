FROM python:3.12-slim

LABEL org.opencontainers.image.title="Edge Payload Guard" \
      org.opencontainers.image.description="Offline-first JSON Schema validator for embedded and IoT telemetry payloads." \
      org.opencontainers.image.source="https://github.com/RONALD-REX-7/edge-payload-guard" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/edge-payload-guard
COPY pyproject.toml README.md LICENSE ./
COPY edge_payload_guard ./edge_payload_guard

RUN python -m pip install --no-cache-dir --disable-pip-version-check . \
    && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /opt/edge-payload-guard

USER 10001:10001
ENTRYPOINT ["edge-payload-guard"]
CMD ["--help"]
