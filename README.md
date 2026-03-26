# LoRaBridge

**Forward LoRaWAN gateway data bidirectionally between ChirpStack and The Things Network (TTN)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What is this?

A lightweight bridge that enables **bidirectional** communication for LoRaWAN gateways:
- **Uplink (↑)**: Gateway data from ChirpStack → TTN & TTN → ChirpStack
- **Downlink (↓)**: Server responses TTN → ChirpStack & ChirpStack → TTN

This allows:
- ✅ Devices from **TTN** to register on **ChirpStack** network
- ✅ Devices from **ChirpStack** to register on **TTN** network  
- ✅ Joint network operation with automatic failover
- ✅ Zero gateway configuration changes

## Key Features

- 🔄 **Bidirectional**: Uplink + Downlink forwarding
- 🌐 **Multi-Gateway**: Automatically detects and tracks all connected gateways
- 🔧 **Zero Gateway Config**: All configuration server-side
- 📡 **JOIN Support**: Devices can successfully join either network
- 🚀 **Lightweight**: Minimal dependencies (paho-mqtt)
- 🐳 **Containerized**: Docker/Compose ready
- 📊 **Logging**: Full message tracking for debugging

## How it works

```
TTN Gateway Network           ChirpStack Network
    ↓ (uplink)                   ↓ (uplink)
    └─────────LoRaBridge─────────┘
              ↕ (bidirectional)
         MQTT & UDP Conversion
    ┌─────────LoRaBridge─────────┐
    ↑ (downlink)                   ↑ (downlink)
TTN application server      ChirpStack application
```

### Protocol Handling
- **Uplink**: MQTT JSON (ChirpStack) ↔ UDP Semtech (TTN)
- **Downlink**: UDP Semtech (TTN) ↔ MQTT JSON (ChirpStack)

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
- Gateway Bridge must use **JSON** marshaling (protobuf not supported)
- Gateways can be registered in either or both ChirpStack and TTN

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
TTN_PORT=1700
CHIRPSTACK_MQTT_HOST=mosquitto
CHIRPSTACK_MQTT_PORT=1883
MQTT_TOPIC=eu868/gateway/+/event/up       # Adjust region (eu868, us915, etc)
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

## Device JOIN Support

### Scenario 1: Device joins TTN network

1. Device sends JOIN request (heard by any gateway)
2. Gateway in ChirpStack network receives uplink
3. Bridge forwards to TTN over UDP
4. TTN's Network Server processes JOIN
5. TTN sends JOIN Accept downlink
6. Bridge forwards back to gateway via ChirpStack MQTT
7. Gateway transmits JOIN Accept to device ✓

### Scenario 2: Device joins ChirpStack network

1. Device sends JOIN request (heard by any gateway)
2. If gateway in TTN network, TTN receives uplink
3. Bridge forwards to ChirpStack via MQTT
4. ChirpStack's Network Server processes JOIN
5. ChirpStack sends JOIN Accept
6. Bridge forwards to gateway via UDP (Semtech)
7. Gateway transmits JOIN Accept to device ✓

## Multiple Gateways

The bridge **automatically detects all gateways**. Just:

1. Add gateway to ChirpStack
2. Add gateway to TTN (same EUI)
3. Configure gateway to point to your server
4. Done! Bridge auto-forwards all data

## Monitoring

Expected output:
```
✓ Connected to ChirpStack MQTT
📡 New gateway detected: fcc23dfffe20f0a7
✓ [fcc23dfffe20f0a7] Uplink to TTN - Freq: 868.1 MHz, RSSI: -91 dBm
✓ [fcc23dfffe20f0a7] Received downlink from TTN - forwarding to ChirpStack
```

## Troubleshooting

### No uplink data in TTN?
- Check Gateway Bridge config has `marshaler="json"`
- Verify gateway is registered in TTN with same EUI
- Check bridge is running: `docker-compose ps` or `systemctl status chirpstack-ttn-bridge`
- View logs: `docker-compose logs -f` or `journalctl -u chirpstack-ttn-bridge -f`

### Device JOIN not working?
- Verify gateway is in both ChirpStack and TTN configs (same EUI)
- Check MQTT connectivity: TTN should receive uplink first
- Verify `MQTT_TOPIC` matches your region (EU868, US915, etc)
- Check device is programmed with correct AppEUI/DevEUI for target network

### Protobuf errors?
- Gateway Bridge config issue
- Ensure `marshaler="json"` is in `[integration]` section
- Restart Gateway Bridge after changing config

### Connection refused errors?
- Check MQTT broker is running
- Verify `CHIRPSTACK_MQTT_HOST` and `CHIRPSTACK_MQTT_PORT`
- TTN UDP port must be open (1700/udp outbound)

## Architecture Details

### Uplink Flow (Device → Network Servers)
```
Device → Gateway → ChirpStack(MQTT/JSON) → Bridge → TTN(UDP/Semtech)
```

### Downlink Flow (Network Servers → Device)  
```
TTN(UDP/Semtech) → Bridge → ChirpStack(MQTT/JSON) → Gateway → Device
```

### Gateway Mapping
- Bridge tracks gateway EUI from MQTT messages
- Dynamic gateway detection (no manual registration)
- Supports unlimited gateways per network
- Bidirectional routing based on packet type

## Files

```
.
├── README.md                          # This file
├── Dockerfile                         # Docker image
├── docker-compose.yml                 # Docker deployment
├── chirpstack-ttn-bridge-docker.py    # Docker version (env vars)
├── chirpstack-ttn-bridge.py           # Standalone version (config)
├── chirpstack-ttn-bridge.service      # Systemd service
├── install.sh                         # Installation script
├── gateway-bridge-config.toml         # Example Gateway Bridge config
├── env.example                        # Environment variables template
└── LICENSE                            # MIT License
```

## Version History

### v2.0 (Current - Bidirectional)
- ✨ Downlink support (TTN → ChirpStack)
- ✨ Downlink support (ChirpStack → TTN)
- ✨ Device JOIN support in both directions
- 🔧 Improved gateway tracking
- 📊 Enhanced logging

### v1.0 (Unidirectional)
- Uplink only (ChirpStack → TTN)

## License

MIT License - see [LICENSE](LICENSE)

## Support & Contributing

Found an issue? Have a suggestion?
- Open an issue on GitHub
- Check existing documentation above

## Credits

- [ChirpStack](https://www.chirpstack.io/) - Open-source LoRaWAN Network Server
- [The Things Network](https://www.thethingsnetwork.org/) - Global LoRaWAN network
- [Semtech LoRaWAN Gateway API](https://github.com/Lora-net/packet_forwarder/blob/master/PROTOCOL.md) - Gateway protocol specification
