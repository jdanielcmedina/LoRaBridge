#!/bin/bash

# ChirpStack to TTN Bridge - Installation Script
# This script installs the bridge service on a Debian/Ubuntu system

set -e

echo "==================================="
echo "ChirpStack to TTN Bridge Installer"
echo "==================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Install Python dependencies
echo "[1/5] Installing Python dependencies..."
apt install -y python3-paho-mqtt

# Copy bridge script
echo "[2/5] Installing bridge script..."
cp chirpstack-ttn-bridge.py /usr/local/bin/
chmod +x /usr/local/bin/chirpstack-ttn-bridge.py

# Copy systemd service
echo "[3/5] Installing systemd service..."
cp chirpstack-ttn-bridge.service /etc/systemd/system/

# Reload systemd
echo "[4/5] Reloading systemd..."
systemctl daemon-reload

# Enable service
echo "[5/5] Enabling service..."
systemctl enable chirpstack-ttn-bridge

echo ""
echo "✅ Installation complete!"
echo ""
echo "⚠️  IMPORTANT: Before starting the service:"
echo "   1. Edit /usr/local/bin/chirpstack-ttn-bridge.py"
echo "   2. Update GATEWAY_EUI with your gateway EUI"
echo "   3. Update TTN_SERVER if not using EU region"
echo ""
echo "To start the service:"
echo "   systemctl start chirpstack-ttn-bridge"
echo ""
echo "To view logs:"
echo "   journalctl -u chirpstack-ttn-bridge -f"
echo ""

