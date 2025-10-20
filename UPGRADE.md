# Upgrade Guide - Multi-Gateway Support

## 🎯 What's New

- ✅ **Automatic multi-gateway support** - No need to configure individual gateway EUIs
- ✅ **Dynamic gateway detection** - Bridge automatically identifies and tracks all gateways
- ✅ **Better logging** - Shows which gateway sent each message
- ✅ **Zero configuration** - Just add gateways to ChirpStack & TTN, they'll work automatically

## 🚀 How to Upgrade

### Option 1: Using the update script (Recommended)

```bash
# 1. Clone/download the repository
git clone https://github.com/jdanielcmedina/GatewayChirpStackTTN.git
cd GatewayChirpStackTTN

# 2. Copy to your server
scp -r * root@wiot.network:/tmp/chirpstack-ttn-bridge-update/

# 3. SSH to server and run update
ssh root@wiot.network
cd /tmp/chirpstack-ttn-bridge-update/
sudo ./update.sh

# 4. Verify it's working
sudo journalctl -u chirpstack-ttn-bridge -f
```

### Option 2: Manual update

```bash
# 1. Backup current script
ssh root@wiot.network
sudo cp /usr/local/bin/chirpstack-ttn-bridge.py /usr/local/bin/chirpstack-ttn-bridge.py.backup

# 2. Copy new script
scp chirpstack-ttn-bridge.py root@wiot.network:/usr/local/bin/

# 3. Restart service
ssh root@wiot.network
sudo systemctl restart chirpstack-ttn-bridge

# 4. Check logs
sudo journalctl -u chirpstack-ttn-bridge -f
```

## 📊 What to Expect After Upgrade

Before (single gateway):
```
✓ Connected to ChirpStack MQTT (rc=0)
✓ Sent uplink to TTN - Freq: 868.1 MHz, RSSI: -91 dBm
```

After (multi-gateway):
```
ChirpStack → TTN Bridge started (JSON mode - Multi-Gateway)
✓ Connected to ChirpStack MQTT (rc=0)

📡 New gateway detected: fcc23dfffe20f0a7
✓ [fcc23dfffe20f0a7] Sent to TTN - Freq: 868.1 MHz, RSSI: -91 dBm

📡 New gateway detected: 0102030405060708
✓ [0102030405060708] Sent to TTN - Freq: 867.3 MHz, RSSI: -105 dBm
```

## 🔧 Adding New Gateways (Post-Upgrade)

After upgrading, adding new gateways is simple:

1. **Register gateway in ChirpStack**
   - Go to ChirpStack web interface
   - Add gateway with its EUI

2. **Register same gateway in TTN**
   - Go to TTN Console
   - Add gateway with same EUI

3. **Configure gateway hardware**
   - Point to: `wiot.network:3001` (Basic Station)
   - Or: `wiot.network:1700` (UDP, if using multiplexer)

4. **Done!**
   - Bridge automatically detects and starts forwarding
   - Check logs to see: `📡 New gateway detected: <EUI>`

## 🐛 Troubleshooting

### Service won't start after upgrade
```bash
# Check error logs
sudo journalctl -u chirpstack-ttn-bridge -n 50

# Verify Python dependencies
sudo apt install python3-paho-mqtt

# Restore backup if needed
sudo cp /usr/local/bin/chirpstack-ttn-bridge.py.backup /usr/local/bin/chirpstack-ttn-bridge.py
sudo systemctl restart chirpstack-ttn-bridge
```

### Gateways not detected
```bash
# 1. Verify MQTT is receiving data
docker exec -it <mosquitto-container> mosquitto_sub -t 'eu868/gateway/+/event/up' -v

# 2. Check if gateway is connected to ChirpStack
# Login to ChirpStack web interface and verify gateway status

# 3. Check Gateway Bridge is using JSON
docker exec <gateway-bridge-container> cat /etc/chirpstack-gateway-bridge/*.toml | grep marshaler
# Should see: marshaler="json"
```

### Data in ChirpStack but not in TTN
```bash
# 1. Verify gateway is registered in TTN with same EUI
# 2. Check bridge is sending
sudo journalctl -u chirpstack-ttn-bridge -f | grep "Sent to TTN"

# 3. Check network connectivity to TTN
ping eu1.cloud.thethings.network
```

## 📝 Rollback

If you need to rollback to single-gateway version:

```bash
# Restore backup
sudo cp /usr/local/bin/chirpstack-ttn-bridge.py.backup /usr/local/bin/chirpstack-ttn-bridge.py

# Edit and set your gateway EUI
sudo nano /usr/local/bin/chirpstack-ttn-bridge.py
# Add: GATEWAY_EUI = 'fcc23dfffe20f0a7'

# Restart
sudo systemctl restart chirpstack-ttn-bridge
```

## 🎉 Success Indicators

✅ Service is active: `systemctl is-active chirpstack-ttn-bridge` returns "active"

✅ Gateways detected: Logs show "📡 New gateway detected: ..."

✅ Data flowing to TTN: Logs show "✓ [gateway_eui] Sent to TTN..."

✅ TTN Console shows traffic: Gateway page in TTN shows recent uplinks

## 📚 More Info

- [README.md](README.md) - Full documentation
- [GitHub Issues](https://github.com/jdanielcmedina/GatewayChirpStackTTN/issues) - Report problems

