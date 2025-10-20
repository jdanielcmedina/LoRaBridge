# 🚀 Quick Start Guide

## For Existing ChirpStack Setup (Docker)

### 1. Add LoRaBridge to Your docker-compose.yml

Add this service to your existing ChirpStack `docker-compose.yml`:

```yaml
services:
  # ... your existing services (chirpstack, mosquitto, postgres, etc.)

  lorabridge:
    image: lorabridge:latest
    build:
      context: ./lorabridge
    restart: unless-stopped
    environment:
      - TTN_SERVER=eu1.cloud.thethings.network
      - TTN_PORT=1700
      - CHIRPSTACK_MQTT_HOST=mosquitto
      - CHIRPSTACK_MQTT_PORT=1883
      - MQTT_TOPIC=eu868/gateway/+/event/up
    networks:
      - default
    depends_on:
      - mosquitto
```

### 2. Clone LoRaBridge

```bash
cd /path/to/your/chirpstack-docker/
git clone https://github.com/jdanielcmedina/LoRaBridge.git lorabridge
```

### 3. Start the Service

```bash
docker-compose up -d lorabridge
docker-compose logs -f lorabridge
```

## For New Installation (Complete Setup)

### Option A: Docker Compose (All-in-One)

```bash
# 1. Clone LoRaBridge
git clone https://github.com/jdanielcmedina/LoRaBridge.git
cd LoRaBridge

# 2. Start everything
docker-compose up -d

# 3. Monitor
docker-compose logs -f
```

### Option B: Add to Existing ChirpStack

```bash
# 1. Navigate to your ChirpStack directory
cd /opt/chirpstack-docker  # or wherever your setup is

# 2. Clone LoRaBridge
git clone https://github.com/jdanielcmedina/LoRaBridge.git lorabridge

# 3. Add to docker-compose.yml (see above)

# 4. Restart
docker-compose up -d
```

## 📝 Configuration Checklist

### ChirpStack Gateway Bridge

✅ **Must use JSON marshaling**

Edit: `/path/to/gateway-bridge-config.toml`
```toml
[integration]
marshaler="json"  # CRITICAL: Must be "json"
```

Restart Gateway Bridge:
```bash
docker restart chirpstack-gateway-bridge-basicstation
```

### Gateway Setup

✅ **Configure gateway to use Basic Station**

In gateway web interface:
- Protocol: **Basic Station**
- Server: `ws://your-server:3001` or `wss://your-server:3001`
- Port: **3001**

### TTN Setup

✅ **Register gateway in TTN Console**

1. Go to [console.cloud.thethings.network](https://console.cloud.thethings.network)
2. Add gateway with **same EUI** as in ChirpStack
3. Frequency plan: Match your region (e.g., Europe 863-870 MHz)

## ✅ Verification

### 1. Check Service is Running

**Docker:**
```bash
docker ps | grep lorabridge
# Should show: Up X minutes
```

**Standalone:**
```bash
systemctl is-active chirpstack-ttn-bridge
# Should output: active
```

### 2. Check Logs for Gateway Detection

```bash
docker logs lorabridge | grep "New gateway detected"
# or
journalctl -u chirpstack-ttn-bridge | grep "New gateway detected"
```

Should see:
```
📡 New gateway detected: a1b2c3d4e5f6a7b8
```

### 3. Check TTN Console

1. Go to your gateway page in TTN Console
2. Click "Live data" tab
3. You should see recent uplinks appearing

### 4. Verify Data Flow

```bash
# Watch logs in real-time
docker logs -f lorabridge
# or
journalctl -u chirpstack-ttn-bridge -f
```

You should see:
```
✓ [gateway_eui] Sent to TTN - Freq: 868.1 MHz, RSSI: -91 dBm
```

## 🎯 Common Scenarios

### Scenario 1: I have ChirpStack running, want to add TTN

```bash
cd /your/chirpstack/directory
git clone https://github.com/jdanielcmedina/LoRaBridge.git lorabridge
# Add service to docker-compose.yml (see above)
docker-compose up -d lorabridge
```

### Scenario 2: Fresh installation of everything

Follow the main [README.md](README.md) for complete setup.

### Scenario 3: Multiple regions (EU + US gateways)

Create two bridge instances:

```yaml
lorabridge-eu:
  image: lorabridge:latest
  environment:
    - TTN_SERVER=eu1.cloud.thethings.network
    - MQTT_TOPIC=eu868/gateway/+/event/up

lorabridge-us:
  image: lorabridge:latest
  environment:
    - TTN_SERVER=nam1.cloud.thethings.network
    - MQTT_TOPIC=us915/gateway/+/event/up
```

## 💡 Tips

- 🔍 **Enable debug mode**: Add `-e LOG_LEVEL=debug` to see more details
- 📊 **Monitor statistics**: Check TTN Console for traffic graphs
- 🔄 **Zero downtime**: Bridge runs independently, won't affect ChirpStack
- 🛑 **Easy disable**: Just stop the container/service

## ❓ Need Help?

- 📖 Read [README.md](README.md) for detailed documentation
- 🆙 Upgrading? See [UPGRADE.md](UPGRADE.md)
- 🐛 Issues? [Report here](https://github.com/jdanielcmedina/LoRaBridge/issues)

---

**Estimated setup time**: 5-10 minutes ⏱️

