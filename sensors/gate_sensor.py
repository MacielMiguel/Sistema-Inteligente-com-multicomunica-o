import time
import json
import random
from broker_producer import get_broker_connection

# Conectar ao broker Kafka
producer = get_broker_connection()

TOPIC = "gates_data"

def read_lock():
    """Simula a leitura de uma fechadura digital"""
    return round(random.uniform(0, 1), 0)  # 0 = fechado, 1 = aberto

while True:
    lock = read_lock()
    if lock == 0:
        message = {
        "device_id": "gate_sensor1",
        "type": "gate",
        "status": "off"
        }   
    else:
        message = {
        "device_id": "gate_sensor1",
        "type": "gate",
        "status": "on"
        }   
    
    # Publicar no broker
    producer.send(TOPIC, json.dumps(message).encode("utf-8"))
    print(f"[Gate Sensor] Sent: {message}")
    
    time.sleep(15)  # Publica a cada 15 segundos
