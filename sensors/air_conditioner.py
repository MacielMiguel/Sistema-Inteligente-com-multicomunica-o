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
temperature = 22
power = "on"
mode = "COOL"
fan_speed = "MEDIUM"
swing = "False"

# Conectar ao broker Kafka
producer = get_broker_connection()

TOPIC = "temperature_data"

def read_temperature():
    # Simula influência da temperatura desejada (exemplo simples)
    temp = temperature + random.uniform(-2, 2)  # Variação de +/- 2 graus
    return int(round(temp, 0))

def receive_commands():
    global temperature, power, mode, fan_speed, swing
    for message in consumer:
        command = message.value
        if command.get("action") == "set_temperature":
            temperature = command.get("temperature")
        if command.get("action") == "set_power":
            power = command.get("power")
            if power:
                power = "on"
                print("Power On")
            else:
                power = "off"
                print("Power Off")
        if command.get("action") == "set_mode":
            mode = command.get("mode")
            match mode:
                case 0: mode = "COOL"
                case 1: mode = "HEAT"
                case 2: mode = "FAN"
                case 3: mode = "DRY"
                case 4: mode = "AUTO"
        if command.get("action") == "set_fan_speed":
            fan_speed = command.get("fan_speed")
            match fan_speed:
                case 0: fan_speed = "LOW"
                case 1: fan_speed = "MEDIUM"
                case 2: fan_speed = "HIGH"
                case 3: fan_speed = "AUTOMATIC"
        if command.get("action") == "set_swing":
            swing = command.get("swing")
            match swing:
                case True: swing = "True"
                case False: swing = "False"

command_thread = threading.Thread(target=receive_commands)
command_thread.daemon = True
command_thread.start()

while True:
    temp = read_temperature()
    message = {
        "device_id": "AC_sensor1",
        "type": "AC",
        "status": power,
        "temperature": temp,
        "mode": mode,
        "fan_speed": fan_speed,
        "swing": swing
        }
    
    # Publicar no broker Kafka
    if power == "on":
        producer.send(TOPIC, json.dumps(message).encode("utf-8"))
        print(f"[AC Sensor] Sent: {message}")
    
    time.sleep(15)  # Publica a cada 15 segundos
