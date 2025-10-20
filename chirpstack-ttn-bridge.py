#!/usr/bin/env python3
import json
import socket
import base64
import time
import struct
from datetime import datetime
import paho.mqtt.client as mqtt

# Configuration
TTN_SERVER = 'eu1.cloud.thethings.network'
TTN_PORT = 1700
CHIRPSTACK_MQTT = '127.0.0.1'
CHIRPSTACK_MQTT_PORT = 1883
MQTT_TOPIC = 'eu868/gateway/+/event/up'

# UDP Socket for TTN
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Track active gateways
active_gateways = set()

print('ChirpStack → TTN Bridge started (JSON mode - Multi-Gateway)')
print('TTN Server: ' + TTN_SERVER + ':' + str(TTN_PORT))
print('Waiting for gateway data...')

def send_to_ttn(data):
    try:
        sock.sendto(data, (TTN_SERVER, TTN_PORT))
        return True
    except Exception as e:
        print('✗ Error sending to TTN: ' + str(e))
        return False

def on_connect(client, userdata, flags, rc):
    print('✓ Connected to ChirpStack MQTT (rc=' + str(rc) + ')')
    client.subscribe(MQTT_TOPIC)
    print('✓ Subscribed to: ' + MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        
        # Extract gateway ID from rxInfo
        rx_info = payload.get('rxInfo', {})
        gateway_id = rx_info.get('gatewayId', '')
        
        if not gateway_id:
            print('✗ No gateway ID in message')
            return
        
        # Track new gateways
        if gateway_id not in active_gateways:
            active_gateways.add(gateway_id)
            print('📡 New gateway detected: ' + gateway_id)
        
        # Extract data
        phy_payload = payload.get('phyPayload', '')
        if not phy_payload:
            return
            
        tx_info = payload.get('txInfo', {})
        
        # Create Semtech UDP packet
        rxpk = {
            'time': rx_info.get('gwTime', datetime.utcnow().isoformat() + 'Z'),
            'tmst': int(time.time() * 1000000) % 4294967296,
            'freq': tx_info.get('frequency', 868100000) / 1000000.0,
            'chan': 0,
            'rfch': 0,
            'stat': 1,
            'modu': 'LORA',
            'datr': 'SF' + str(tx_info.get('modulation', {}).get('lora', {}).get('spreadingFactor', 7)) + 'BW' + str(tx_info.get('modulation', {}).get('lora', {}).get('bandwidth', 125)),
            'codr': '4/5',
            'rssi': int(rx_info.get('rssi', -120)),
            'lsnr': float(rx_info.get('snr', 0)),
            'size': len(base64.b64decode(phy_payload)),
            'data': phy_payload
        }
        
        packet = {'rxpk': [rxpk]}
        
        # Create Semtech UDP packet (PUSH_DATA)
        protocol_version = bytes([0x02])
        token = struct.pack('>H', int(time.time()) % 65536)
        identifier = bytes([0x00])  # PUSH_DATA
        gateway_eui = bytes.fromhex(gateway_id)  # Use dynamic gateway ID
        json_data = json.dumps(packet).encode('utf-8')
        
        udp_packet = protocol_version + token + identifier + gateway_eui + json_data
        send_to_ttn(udp_packet)
        
        print('✓ [' + gateway_id + '] Sent to TTN - Freq: ' + str(rxpk['freq']) + ' MHz, RSSI: ' + str(rxpk['rssi']) + ' dBm')
        
    except Exception as e:
        print('✗ Error processing message: ' + str(e))

# MQTT Client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print('Connecting to ChirpStack MQTT at ' + CHIRPSTACK_MQTT + ':' + str(CHIRPSTACK_MQTT_PORT) + '...')
client.connect(CHIRPSTACK_MQTT, CHIRPSTACK_MQTT_PORT, 60)

print('Starting MQTT loop...')
client.loop_forever()
