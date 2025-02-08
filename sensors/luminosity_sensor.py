import time
import json
import random
from broker_producer import get_broker_connection

# Conectar ao broker Kafka
producer = get_broker_connection()

TOPIC = "luminosity_data"

def read_luminosity():
    """Simula a leitura de um sensor de luminosidade"""
    return round(random.uniform(100, 1000), 2)  # Luminosidade em lux

while True:
    luminosity = read_luminosity()
    message = {"sensor": "luminosity_sensor", "luminosity": luminosity}
    
    # Publicar no broker
    producer.send(TOPIC, json.dumps(message).encode("utf-8"))
    print(f"[Luminosity Sensor] Sent: {message}")
    
    time.sleep(15)  # Publica a cada 15 segundos
