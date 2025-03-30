# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
import paho.mqtt.client as mqtt
import base64
import os

# Encryption Key (Must be 16, 24, or 32 bytes long)
SECRET_KEY = b'1234567890123456'  # 16-byte key for AES-128
IV = os.urandom(16)  # Generate a random IV

def encrypt_message(message):
    """Encrypts a message using AES encryption."""
    cipher = AES.new(SECRET_KEY, AES.MODE_CFB, IV)
    encrypted_bytes = cipher.encrypt(message.encode('utf-8'))
    return base64.b64encode(IV + encrypted_bytes).decode('utf-8')

def decrypt_message(encrypted_message):
    """Decrypts a message using AES encryption."""
    encrypted_data = base64.b64decode(encrypted_message)
    iv = encrypted_data[:16]
    cipher = AES.new(SECRET_KEY, AES.MODE_CFB, iv)
    decrypted_bytes = cipher.decrypt(encrypted_data[16:])
    return decrypted_bytes.decode('utf-8')

# MQTT Configuration
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "iot/security/sensor"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker!")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"\n[Attacker] Intercepted Data (Raw): {msg.payload.decode()}")
    try:
        decrypted_data = decrypt_message(msg.payload.decode())
        print(f"[Decrypted] Sensor Data: {decrypted_data}")
    except Exception as e:
        print("[Warning] Unable to decrypt message - possibly intercepted!")

# Simulated IoT Device (Publishes Data)
client_pub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client_pub.connect(BROKER, PORT, 60)

iot_data = "Temperature: 25C, Humidity: 60%"
encrypted_data = encrypt_message(iot_data)
print(f"\n[IoT Device] Sending Encrypted Data: {encrypted_data}")
client_pub.publish(TOPIC, encrypted_data)

# Attacker Listener (Intercepts Messages)
client_sub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client_sub.on_connect = on_connect
client_sub.on_message = on_message
client_sub.connect(BROKER, PORT, 60)

client_sub.loop_start()
