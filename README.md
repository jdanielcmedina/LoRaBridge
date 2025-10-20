# LoRaBridge - ChirpStack to TTN Gateway Bridge

<div align="center">

**Forward LoRaWAN gateway data from ChirpStack to The Things Network simultaneously**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)

</div>

---

## 🎯 Overview

**LoRaBridge** allows your LoRaWAN gateways to communicate with **two network servers simultaneously**:
- **ChirpStack** (your private server)
- **The Things Network** (global community network)

Perfect for:
- 🌐 Contributing to public LoRaWAN networks while maintaining private infrastructure
- 🔄 Migrating from TTN to ChirpStack without downtime
- 🧪 Testing and development across multiple network servers
- 📊 Comparing network server performance

## ✨ Features

- ✅ **Multi-gateway support** - Automatically handles unlimited gateways
- ✅ **Zero gateway configuration** - All setup done on the server side
- ✅ **Docker & Standalone** - Choose your preferred deployment method
- ✅ **Auto-discovery** - Detects new gateways automatically
- ✅ **Production-ready** - Lightweight, stable, tested
- ✅ **Easy deployment** - One-command installation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│         LoRaWAN Gateways (Basic Station)                │
│  • Lorix One  • RAK  • Dragino  • MultiTech  • etc      │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ WebSocket (port 3001)
                         │
┌────────────────────────▼────────────────────────────────┐
│         ChirpStack Gateway Bridge (Docker)              │
│  Converts: WebSocket → MQTT (JSON)                      │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ MQTT (JSON format)
                         │
         ┌───────────────┴────────────────┐
         │                                │
         ▼                                ▼
┌────────────────┐            ┌──────────────────────┐
│   ChirpStack   │            │   LoRaBridge         │
│   (Docker)     │            │   (This Service)     │
│                │            │  • Reads MQTT        │
│  • Devices     │            │  • Converts to UDP   │
│  • Applications│            │  • Forwards to TTN   │
│  • Integrations│            └──────────┬───────────┘
└────────────────┘                       │
                                         │ UDP (port 1700)
                                         │
                              ┌──────────▼──────────┐
                              │  The Things Network │
                              │  (eu1.cloud...)     │
                              └─────────────────────┘
```

## 🚀 Quick Start

### Docker Deployment (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/jdanielcmedina/LoRaBridge.git
cd LoRaBridge

# 2. Configure environment (optional - defaults are usually fine)
cp env.example .env
nano .env  # Adjust TTN region if not in Europe

# 3. Start the bridge
docker-compose up -d

# 4. Check logs
docker-compose logs -f chirpstack-ttn-bridge
```

### Standalone Deployment

```bash
# 1. Clone repository
git clone https://github.com/jdanielcmedina/LoRaBridge.git
cd LoRaBridge

# 2. Run installation script
sudo ./install.sh

# 3. Start service
sudo systemctl start chirpstack-ttn-bridge

# 4. Check logs
sudo journalctl -u chirpstack-ttn-bridge -f
```

## 📋 Prerequisites

### Required
- **ChirpStack 4.x** running with Docker
- **ChirpStack Gateway Bridge** (BasicStation mode)
- **Mosquitto MQTT broker** (included in ChirpStack Docker)
- **Gateway registered in both ChirpStack and TTN**

### Gateway Bridge Configuration
**CRITICAL**: Gateway Bridge must use JSON marshaling. Edit your configuration:

```toml
[integration]
marshaler="json"  # MUST be "json", not "protobuf"
```

See [gateway-bridge-config.toml](gateway-bridge-config.toml) for complete example.

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TTN_SERVER` | `eu1.cloud.thethings.network` | TTN server address |
| `TTN_PORT` | `1700` | TTN UDP port |
| `CHIRPSTACK_MQTT_HOST` | `mosquitto` | MQTT broker hostname |
| `CHIRPSTACK_MQTT_PORT` | `1883` | MQTT broker port |
| `MQTT_TOPIC` | `eu868/gateway/+/event/up` | MQTT topic pattern |

### TTN Region Servers

| Region | Server |
|--------|--------|
| 🇪🇺 Europe | `eu1.cloud.thethings.network` |
| 🇺🇸 North America | `nam1.cloud.thethings.network` |
| 🇦🇺 Australia | `au1.cloud.thethings.network` |

### Adding Multiple Gateways

The bridge **automatically detects and forwards all gateways**. No configuration needed!

1. **Add gateway to ChirpStack** - Web interface
2. **Add gateway to TTN** - Console (same EUI)
3. **Configure gateway** - Point to your server (port 3001, Basic Station)
4. **Done!** - Bridge auto-detects and forwards

## 📊 Monitoring

### Docker Deployment

```bash
# View logs
docker-compose logs -f chirpstack-ttn-bridge

# Check status
docker-compose ps

# Restart service
docker-compose restart chirpstack-ttn-bridge
```

### Standalone Deployment

```bash
# View logs
sudo journalctl -u chirpstack-ttn-bridge -f

# Check status
sudo systemctl status chirpstack-ttn-bridge

# Restart service
sudo systemctl restart chirpstack-ttn-bridge
```

### Expected Output

```
======================================================
ChirpStack → TTN Bridge (Multi-Gateway Support)
======================================================
TTN Server: eu1.cloud.thethings.network:1700
MQTT Broker: mosquitto:1883
MQTT Topic: eu868/gateway/+/event/up
Waiting for gateway data...
======================================================
✓ Connected to ChirpStack MQTT
✓ Subscribed to: eu868/gateway/+/event/up

📡 New gateway detected: a1b2c3d4e5f6a7b8
   Active gateways: 1
✓ [a1b2c3d4e5f6a7b8] Sent to TTN - Freq: 868.1 MHz, RSSI: -91 dBm

📡 New gateway detected: 1122334455667788
   Active gateways: 2
✓ [1122334455667788] Sent to TTN - Freq: 867.3 MHz, RSSI: -105 dBm
```

## 🐳 Docker Compose Integration

### Add to Existing ChirpStack Setup

```yaml
# Add this to your existing docker-compose.yml

services:
  # ... your existing services (chirpstack, mosquitto, etc.)

  chirpstack-ttn-bridge:
    image: lorabridge:latest
    build: ./lorabridge
    restart: unless-stopped
    environment:
      - TTN_SERVER=eu1.cloud.thethings.network
      - CHIRPSTACK_MQTT_HOST=mosquitto
      - MQTT_TOPIC=eu868/gateway/+/event/up
    networks:
      - default
```

## 🐛 Troubleshooting

### No data in TTN

<details>
<summary>Click to expand</summary>

**Checklist:**
1. ✅ Gateway registered in TTN with correct EUI
2. ✅ Gateway Bridge using `marshaler="json"` (not protobuf)
3. ✅ Service is running: `docker ps` or `systemctl status`
4. ✅ Logs show data: `docker logs` or `journalctl`

**Verify Gateway Bridge marshaler:**
```bash
docker exec <gateway-bridge-container> cat /etc/chirpstack-gateway-bridge/*.toml | grep marshaler
# Should output: marshaler="json"
```

</details>

### Protobuf decode errors

<details>
<summary>Click to expand</summary>

This means Gateway Bridge is not using JSON format.

**Fix:**
```bash
# 1. Edit Gateway Bridge config
nano /path/to/gateway-bridge-config.toml

# 2. Ensure this line exists at top of [integration] section:
[integration]
marshaler="json"

# 3. Restart Gateway Bridge
docker restart <gateway-bridge-container>
```

</details>

### MQTT connection refused

<details>
<summary>Click to expand</summary>

**Check Mosquitto:**
```bash
# Verify Mosquitto is running
docker ps | grep mosquitto

# Check if bridge can reach it
docker exec chirpstack-ttn-bridge ping mosquitto

# For standalone: ensure host can connect
telnet localhost 1883
```

</details>

## 🔄 Updating

### Docker
```bash
git pull
docker-compose build --no-cache
docker-compose up -d
```

### Standalone
```bash
git pull
sudo ./update.sh
```

## 📁 Repository Structure

```
LoRaBridge/
├── README.md                          # This file
├── UPGRADE.md                         # Upgrade guide
├── Dockerfile                         # Docker image definition
├── docker-compose.yml                 # Docker Compose configuration
├── chirpstack-ttn-bridge-docker.py    # Docker version (env vars)
├── chirpstack-ttn-bridge.py           # Standalone version
├── chirpstack-ttn-bridge.service      # Systemd service
├── gateway-bridge-config.toml         # Example Gateway Bridge config
├── install.sh                         # Standalone installation script
├── update.sh                          # Update script
└── env.example                        # Environment variables template
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- [ChirpStack](https://www.chirpstack.io/) - Open-source LoRaWAN Network Server
- [The Things Network](https://www.thethingsnetwork.org/) - Global LoRaWAN network
- Community contributors

## 📞 Support

- 🐛 [Report Issues](https://github.com/jdanielcmedina/LoRaBridge/issues)
- 💬 [Discussions](https://github.com/jdanielcmedina/LoRaBridge/discussions)
- 📖 [Wiki](https://github.com/jdanielcmedina/LoRaBridge/wiki)

## ⭐ Star History

If this project helped you, please consider giving it a star!

---

<div align="center">
Made with ❤️ for the LoRaWAN community
</div>
