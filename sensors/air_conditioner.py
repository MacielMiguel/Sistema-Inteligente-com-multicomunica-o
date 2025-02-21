import time
import json
import random
from broker_producer import get_broker_connection
from kafka import KafkaConsumer
import threading

# Configuração do tópico de comandos
COMMAND_TOPIC = "temperature_commands"
BROKER_URL = "localhost:9092"
consumer =  KafkaConsumer(COMMAND_TOPIC, bootstrap_servers=BROKER_URL,
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))
temperature = None

# Conectar ao broker Kafka
producer = get_broker_connection()

TOPIC = "temperature_data"

def read_temperature():
    """Simula a leitura de um sensor de temperatura"""
    if temperature is not None:
        # Simula influência da temperatura desejada (exemplo simples)
        temp = temperature + random.uniform(-2, 2)  # Variação de +/- 2 graus
    else:
        temp = random.uniform(20.0, 30.0)
    return round(temp, 2)

def receive_commands():
    global temperature
    for message in consumer:
        command = message.value
        if command.get("action") == "set_temperature":
            temperature = command.get("temperature")
            print(f"[Temperature Sensor] Received command: {command}")

command_thread = threading.Thread(target=receive_commands)
command_thread.daemon = True
command_thread.start()

while True:
    temp = read_temperature()
    message = {
        "device_id": "AC_sensor1",
        "type": "AC",
        "status": "on",
        "temperature": temp
        } 
    
    # Publicar no broker Kafka
    producer.send(TOPIC, json.dumps(message).encode("utf-8"))
    print(f"[AC Sensor] Sent: {message}")
    
    time.sleep(15)  # Publica a cada 15 segundos
