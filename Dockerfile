# ChirpStack to TTN Bridge - Docker Image
FROM python:3.11-slim

LABEL maintainer="J. Daniel C. Medina"
LABEL description="Bridge service to forward ChirpStack gateway data to The Things Network"

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir paho-mqtt

# Copy bridge script
COPY chirpstack-ttn-bridge-docker.py /app/bridge.py

# Run as non-root user
RUN useradd -m -u 1000 bridge && \
    chown -R bridge:bridge /app

USER bridge

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD pgrep -f bridge.py || exit 1

CMD ["python3", "-u", "/app/bridge.py"]

