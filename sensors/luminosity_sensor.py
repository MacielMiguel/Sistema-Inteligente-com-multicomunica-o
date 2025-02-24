import time
import json
import random
from broker_producer import get_broker_connection
import uuid, socket
from kafka import KafkaConsumer, KafkaProducer
import threading

MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT_RECEIVE = 4991
MULTICAST_PORT_SEND = 4990

sensor_id = str(uuid.uuid4())
status = "on"
device_id = "luminosity"

'''Tudo da parte de Multicast'''
def send_discovery_message():
    message_multicast = {
        "sensor_id": sensor_id,
        "sensor_type": "luminosity",  
        "sensor_name": "lamp_inicial"
    }
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.sendto(json.dumps(message_multicast).encode('utf-8'), (MULTICAST_GROUP, MULTICAST_PORT_SEND))
    print("Mensagem de descoberta enviada")
    sock.close()

def receive_response():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MULTICAST_PORT_RECEIVE))
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

def read_luminosity():
    return round(random.uniform(100, 1000), 2)  # luminosidade em lux

def receive_commands():
    global device_id, status
    for message in consumer:
        command = message.value
        if command.get("device_id") == device_id:
            action = command.get("action")
            if action == "ligar":
                status = "on"
                print("Power On")
            else:
                status = "off"
                print("Power Off")

command_thread = threading.Thread(target=receive_commands)
command_thread.daemon = True
command_thread.start()

while True:
    luminosity = read_luminosity()
    message = {
        "device_id": device_id,
        "type": "luminosity",
        "status": status
        }
    
    if status == "on":
        producer.send(TOPIC, key=message["device_id"].encode("utf-8"), value=message)
        print(f"[Luminosity Sensor] Sent: {message}")
    
    time.sleep(15)
