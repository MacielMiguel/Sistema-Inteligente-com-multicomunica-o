import time
import json
import random
from broker_producer import get_broker_connection

# Conectar ao broker Kafka
producer = get_broker_connection()

TOPIC = "temperature_data"

def read_temperature():
    """Simula a leitura de um sensor de temperatura"""
    return round(random.uniform(20.0, 30.0), 2)

while True:
    temp = read_temperature()
    message = {"sensor": "temperature_sensor", "temperature": temp}
    
    # Publicar no broker Kafka
    producer.send(TOPIC, json.dumps(message).encode("utf-8"))
    print(f"[Temperature Sensor] Sent: {message}")
    
    time.sleep(15)  # Publica a cada 15 segundos
