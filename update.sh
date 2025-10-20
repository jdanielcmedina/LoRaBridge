#!/bin/bash

# ChirpStack to TTN Bridge - Update Script
# Updates the bridge service with latest version

set -e

echo "==================================="
echo "ChirpStack to TTN Bridge Updater"
echo "==================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Backup existing script
if [ -f "/usr/local/bin/chirpstack-ttn-bridge.py" ]; then
    echo "[1/4] Backing up existing script..."
    cp /usr/local/bin/chirpstack-ttn-bridge.py /usr/local/bin/chirpstack-ttn-bridge.py.backup
    echo "✓ Backup saved to /usr/local/bin/chirpstack-ttn-bridge.py.backup"
fi

# Copy new script
echo "[2/4] Installing updated script..."
cp chirpstack-ttn-bridge.py /usr/local/bin/
chmod +x /usr/local/bin/chirpstack-ttn-bridge.py

# Restart service
echo "[3/4] Restarting service..."
systemctl restart chirpstack-ttn-bridge

# Check status
echo "[4/4] Checking service status..."
sleep 2
if systemctl is-active --quiet chirpstack-ttn-bridge; then
    echo "✅ Service is running!"
else
    echo "⚠️  Service failed to start. Check logs:"
    echo "   journalctl -u chirpstack-ttn-bridge -n 50"
    exit 1
fi

echo ""
echo "✅ Update complete!"
echo ""
echo "To view logs:"
echo "   journalctl -u chirpstack-ttn-bridge -f"
echo ""
echo "Changes in this version:"
echo "  • Multi-gateway support (automatic detection)"
echo "  • Dynamic gateway EUI extraction"
echo "  • Better logging with gateway identification"
echo ""

