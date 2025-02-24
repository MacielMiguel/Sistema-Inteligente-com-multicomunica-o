import time
import json
import random
from broker_producer import get_broker_connection
from kafka import KafkaConsumer, KafkaProducer
import threading
import socket, uuid

# Informações multicast
MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT_RECEIVE = 4991  # Porta para receber mensagens de resposta
MULTICAST_PORT_SEND = 4990    # Porta para enviar mensagens de descoberta

sensor_id = str(uuid.uuid4())

'''
# Configuração do tópico de comandos
COMMAND_TOPIC = "temperature_commands"
BROKER_URL = "localhost:9092"
'''

# Conectar ao broker Kafka
# producer = get_broker_connection()
TOPIC = None
COMMAND_TOPIC = None
BROKER_URL = None

# Informações do AC
device_id = "AC_sensor" 
temperature = 22
power = "on"
mode = "COOL"
fan_speed = "MEDIUM"
swing = "False"

'''Tudo da parte de Multicast'''
def send_discovery_message():
    message_multicast = {
        "sensor_id": sensor_id,
        "sensor_type": "AC",  
        "sensor_name": "AC_inicial"
    }
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.sendto(json.dumps(message_multicast).encode('utf-8'), (MULTICAST_GROUP, MULTICAST_PORT_SEND))
    print("Mensagem de descoberta enviada")
    sock.close()

def receive_response():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MULTICAST_PORT_RECEIVE))  # Ouvir na porta multicast
    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        response = json.loads(data.decode('utf-8'))
        print("Ouvindo na porta 4991")
        return response
    except socket.timeout:
        print("Timeout aguardando resposta multicast")
        return None
    finally:
        sock.close()

# Loop multicast
while True:
    send_discovery_message()
    response = receive_response()
    if response and response.get("sensor_id") == sensor_id:
        TOPIC = response.get("topic")
        device_id = response.get("sensor_name")
        BROKER_URL = response.get("broker_url")
        COMMAND_TOPIC = response.get("command_topic")
        print(f"Sensor registrado. Tópico> {TOPIC}, Novo nome: {device_id}")
        break
    time.sleep(2)
    
consumer =  KafkaConsumer(COMMAND_TOPIC, bootstrap_servers=[BROKER_URL],
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))
producer = KafkaProducer(bootstrap_servers=[BROKER_URL],
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))


'''Tudo da parte de Kafka'''
def read_temperature():
    temp = temperature

    # Efeito do modo de operação
    if mode == "COOL":
        temp -= 5  # Exemplo: resfria 5 graus abaixo da temperatura desejada
    elif mode == "HEAT":
        temp += 5  # Exemplo: aquece 5 graus acima da temperatura desejada

    # Efeito do swing
    if swing:
        temp += random.uniform(-1, 1) 

    # Efeito da velocidade do ventilador
    if fan_speed == "LOW":
        temp += random.uniform(-0.5, 0.5)  
    elif fan_speed == "MEDIUM":
        temp += random.uniform(-1, 1) 
    elif fan_speed == "HIGH":
        temp += random.uniform(-1.5, 1.5) 

    temp += random.uniform(-2, 2)

    return int(round(temp, 0))

def receive_commands():
    global device_id, temperature, power, mode, fan_speed, swing
    for message in consumer:
        command = message.value
        if command.get("device_id") == device_id:
            # Determina a temperatura
            temperature = command.get("temperature")
            
            # Determina o power
            power = command.get("power")
            if power:
                power = "on"
                print("Power On")
            else:
                power = "off"
                print("Power Off")
            
            # Determina o mode
            mode = command.get("mode")
            match mode:
                case 0: mode = "COOL"
                case 1: mode = "HEAT"
                case 2: mode = "FAN"
                case 3: mode = "DRY"
                case 4: mode = "AUTO"

            # Determina a fan_speed
            fan_speed = command.get("fan_speed")
            match fan_speed:
                case 0: fan_speed = "LOW"
                case 1: fan_speed = "MEDIUM"
                case 2: fan_speed = "HIGH"
                case 3: fan_speed = "AUTOMATIC"

            # Determina o swing
            swing = command.get("swing")
            match swing:
                case True: swing = "True"
                case False: swing = "False"

command_thread = threading.Thread(target=receive_commands)
command_thread.daemon = True
command_thread.start()

# Loop após recebimento de informações
while True:
    temp = read_temperature()
    message = {
        "device_id": device_id,
        "type": "AC",
        "status": power,
        "temperature": temp,
        "mode": mode,
        "fan_speed": fan_speed,
        "swing": swing
        }
    
    # Publicar no broker Kafka
    if power == "on":
        producer.send(TOPIC, key=message["device_id"].encode("utf-8"), value=message)
        print(f"[AC Sensor] Sent: {message}")
    
    time.sleep(15)  # Publica a cada 15 segundos