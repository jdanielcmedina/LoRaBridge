# LoRaBridge

**Forward LoRaWAN gateway data from ChirpStack to The Things Network simultaneously**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What is this?

A lightweight bridge that allows your LoRaWAN gateways to send data to **two network servers at once**:
- **ChirpStack** (your private server)
- **The Things Network** (public community network)

All configuration happens on the server - **zero changes needed on your gateways**.

## How it works

```
Gateway (Basic Station) 
    ↓ WebSocket
ChirpStack Gateway Bridge
    ↓ MQTT (JSON)
    ├→ ChirpStack ✅
    └→ LoRaBridge → TTN ✅
```

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/jdanielcmedina/LoRaBridge.git
cd LoRaBridge
docker-compose up -d
```

### Standalone

```bash
git clone https://github.com/jdanielcmedina/LoRaBridge.git
cd LoRaBridge
sudo ./install.sh
```

## Requirements

- ChirpStack 4.x with Gateway Bridge (Basic Station)
- Gateway Bridge must use JSON marshaling (see below)
- Gateways registered in both ChirpStack and TTN

## Configuration

### 1. Gateway Bridge (CRITICAL)

Edit your Gateway Bridge config and add:

```toml
[integration]
marshaler="json"  # Must be "json", not "protobuf"
```

Then restart Gateway Bridge container.

### 2. Environment Variables

Copy `env.example` to `.env` and adjust if needed:

```bash
TTN_SERVER=eu1.cloud.thethings.network  # Change region if needed
CHIRPSTACK_MQTT_HOST=mosquitto
MQTT_TOPIC=eu868/gateway/+/event/up
```

### 3. Start

**Docker:**
```bash
docker-compose up -d
docker-compose logs -f
```

**Standalone:**
```bash
sudo systemctl start chirpstack-ttn-bridge
sudo journalctl -u chirpstack-ttn-bridge -f
```

## Multiple Gateways

The bridge **automatically detects all gateways**. Just:

1. Add gateway to ChirpStack
2. Add gateway to TTN (same EUI)
3. Configure gateway to point to your server
4. Done! Bridge auto-forwards

## Monitoring

Expected output:
```
✓ Connected to ChirpStack MQTT
📡 New gateway detected: fcc23dfffe20f0a7
✓ [fcc23dfffe20f0a7] Sent to TTN - Freq: 868.1 MHz, RSSI: -91 dBm
```

## Troubleshooting

**No data in TTN?**
- Check Gateway Bridge config has `marshaler="json"`
- Verify gateway is registered in TTN with same EUI
- Check logs: `docker-compose logs -f` or `journalctl -u chirpstack-ttn-bridge -f`

**Protobuf errors?**
- Gateway Bridge config issue - ensure `marshaler="json"` is in `[integration]` section
- Restart Gateway Bridge after changing config

## Files

```
.
├── README.md                          # This file
├── Dockerfile                         # Docker image
├── docker-compose.yml                 # Docker deployment
├── chirpstack-ttn-bridge-docker.py    # Docker version
├── chirpstack-ttn-bridge.py           # Standalone version
├── chirpstack-ttn-bridge.service      # Systemd service
├── install.sh                         # Installation script
├── gateway-bridge-config.toml         # Example config
└── env.example                        # Environment template
```

## License

MIT License - see [LICENSE](LICENSE)

## Credits

- [ChirpStack](https://www.chirpstack.io/) - Open-source LoRaWAN Network Server
- [The Things Network](https://www.thethingsnetwork.org/) - Global LoRaWAN network
