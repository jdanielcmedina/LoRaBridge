#!/usr/bin/env python3
import json
import socket
import base64
import time
import struct
import threading
from datetime import datetime
import paho.mqtt.client as mqtt

# Configuration
TTN_SERVER = 'eu1.cloud.thethings.network'
TTN_PORT = 1700
CHIRPSTACK_MQTT = '127.0.0.1'
CHIRPSTACK_MQTT_PORT = 1883
MQTT_TOPIC = 'eu868/gateway/+/event/up'

# UDP Socket for TTN (bidirectional)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 1700))  # Bind to port 1700 to receive downlink from TTN
sock.settimeout(0)  # Non-blocking mode

# Track active gateways and their addresses
active_gateways = {}  # {gateway_id: {'address': ip, 'port': port, 'last_seen': timestamp}}
gateway_id_to_eui = {}  # Map gateway_id to EUI for reverse lookup

print('ChirpStack ↔ TTN Bridge started (Bidirectional - JSON mode)')
print('TTN Server: ' + TTN_SERVER + ':' + str(TTN_PORT))
print('Local UDP listener: 0.0.0.0:1700 (for TTN downlink)')
print('Waiting for gateway data...')

def send_to_ttn(data, ttn_addr=(TTN_SERVER, TTN_PORT)):
    try:
        sock.sendto(data, ttn_addr)
        return True
    except Exception as e:
        print('✗ Error sending to TTN: ' + str(e))
        return False

def send_to_chirpstack(gateway_id, data):
    """Send downlink data to ChirpStack via MQTT for a specific gateway"""
    try:
        # Topic for ChirpStack downlink: eu868/gateway/{gatewayId}/event/down
        topic = MQTT_TOPIC.replace('/event/up', '/event/down').replace('+', gateway_id)
        
        downlink_payload = {
            'itemsToSend': [{
                'phyPayload': data,
                'txInfo': {
                    'frequency': 868100000,
                    'modulation': {
                        'lora': {
                            'spreadingFactor': 7,
                            'bandwidth': 125000,
                            'codeRate': '4/5'
                        }
                    },
                    'power': 14,
                    'timing': {'delay': {'duration': '1000000000'}}  # 1 second delay
                }
            }]
        }
        
        mqtt_client.publish(topic, json.dumps(downlink_payload), qos=1)
        print('✓ [' + gateway_id + '] Sent downlink to ChirpStack')
        return True
    except Exception as e:
        print('✗ Error sending to ChirpStack: ' + str(e))
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
        
        # Track new gateways with their info
        if gateway_id not in active_gateways:
            active_gateways[gateway_id] = {
                'last_seen': time.time()
            }
            gateway_id_to_eui[gateway_id] = gateway_id
            print('📡 New gateway detected: ' + gateway_id)
        else:
            active_gateways[gateway_id]['last_seen'] = time.time()
        
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
        
        print('✓ [' + gateway_id + '] Uplink to TTN - Freq: ' + str(rxpk['freq']) + ' MHz, RSSI: ' + str(rxpk['rssi']) + ' dBm')
        
    except Exception as e:
        print('✗ Error processing message: ' + str(e))

# MQTT Client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
mqtt_client = client  # Global reference for sending

print('Connecting to ChirpStack MQTT at ' + CHIRPSTACK_MQTT + ':' + str(CHIRPSTACK_MQTT_PORT) + '...')
client.connect(CHIRPSTACK_MQTT, CHIRPSTACK_MQTT_PORT, 60)

def receive_ttn_downlink():
    """Listen for downlink packets from TTN via UDP and forward to ChirpStack"""
    print('✓ TTN downlink listener thread started')
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            
            if len(data) < 12:
                continue
            
            # Parse Semtech packet
            protocol_version = data[0]
            token = struct.unpack('>H', data[1:3])[0]
            identifier = data[3]
            gateway_eui = data[4:12].hex()
            
            # PULL_RESP (identifier 0x03) contains downlink data
            if identifier == 0x03 and len(data) > 12:
                try:
                    json_data = json.loads(data[12:].decode('utf-8'))
                    txpk = json_data.get('txpk', {})
                    
                    if txpk and 'data' in txpk:
                        phy_payload = txpk['data']
                        # Find gateway by EUI
                        gateway_id = None
                        for gw_id, eui in gateway_id_to_eui.items():
                            if eui == gateway_eui or gateway_eui in gw_id:
                                gateway_id = gw_id
                                break
                        
                        if gateway_id:
                            send_to_chirpstack(gateway_id, phy_payload)
                            print('✓ [' + gateway_id + '] Received downlink from TTN - forwarding to ChirpStack')
                        else:
                            print('⚠ Downlink from TTN but no matching gateway found (' + gateway_eui + ')')
                except json.JSONDecodeError:
                    print('⚠ Failed to decode TTN downlink JSON')
            
            # Send PULL_ACK back to TTN
            elif identifier == 0x02:  # PUSH_DATA from TTN gateway
                ack_packet = struct.pack('>BHB', 0x02, token, 0x01)  # 0x01 = PUSH_ACK
                sock.sendto(ack_packet, addr)
        
        except socket.timeout:
            time.sleep(0.1)
        except Exception as e:
            print('✗ Error in TTN downlink listener: ' + str(e))
            time.sleep(1)

# Start downlink listener thread
downlink_thread = threading.Thread(target=receive_ttn_downlink, daemon=True)
downlink_thread.start()

print('Starting MQTT loop...')
client.loop_forever()
