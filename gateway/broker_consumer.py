from kafka import KafkaConsumer
import redis
import threading
import json, socket

MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT_RECEIVE = 4990  # Porta para receber mensagens de descoberta
MULTICAST_PORT_SEND = 4991   # Porta para enviar mensagens de resposta

redis_host = 'localhost'
redis_port = 6379
redis_db = 0
try:
    r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
except redis.exceptions.ConnectionError as e:
    print(f"Erro ao conectar ao Redis: {e}")

def process_discovery_message(message, addr):
    try:
        if isinstance(message, bytes):
            message = message.decode()
        data = json.loads(message)
        sensor_id = data.get("sensor_id")
        sensor_name = data.get("sensor_name")
        sensor_type = data.get("sensor_type")
        topic = None
        command_topic = None

        if sensor_type == "AC":
            AC_id_suf = 0
            while (r.hexists("devices", "AC_sensor" + str(AC_id_suf))):
                AC_id_suf += 1
            sensor_name = "AC_sensor" + str(AC_id_suf)
            topic = "temperature_data"
            command_topic = "temperature_commands"
        elif sensor_type == "luminosity":
            lamp_id_suf = 0
            while (r.hexists("devices", "luminosity_" + str(lamp_id_suf))):
                lamp_id_suf += 1
            sensor_name = "luminosity_" + str(lamp_id_suf)
            topic = "luminosity_data"
            command_topic = "luminosity_commands"
            
        device_data = {"name": sensor_name, "type": sensor_type}

        response = {
            "sensor_id": sensor_id,
            "topic": topic,
            "sensor_name": sensor_name,
            "broker_url": "localhost:9092",
            "command_topic": command_topic
        }

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.sendto(json.dumps(response).encode('utf-8'), (addr[0], MULTICAST_PORT_SEND))
        print("Mensagem de resposta multicast enviada")
        sock.close()

        # Inseri dados iniciais no Redis
        device_id = sensor_name
        r.hset("devices", device_id, json.dumps(device_data))
        print(f"Sensor {sensor_id} registrado/atualizado: {device_data}")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da mensagem de descoberta: {e}")
    except Exception as e:
        print(f"Erro ao processar mensagem de descoberta: {e}")

# Função para consumir mensagens de descoberta por multicast
def consume_discovery_messages():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MULTICAST_PORT_RECEIVE))  # Bind na porta multicast
    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print("Bind feito ao grupo multicast. Escutando...")

    while True:
        data, addr = sock.recvfrom(1024)
        # message = json.loads(data.decode('utf-8'))
        process_discovery_message(data, addr)

def process_message(message, topic):
    try:
        print(f"Mensagem recebida do tópico {topic}: {message.value.decode()}")
        data = json.loads(message.value.decode())
        device_id = data.get("device_id")
        status = data.get("status")
        device_type = data.get("type")

        device_data = {"status": status, "type": device_type}
        if device_type == "AC":
            device_data["temperature"] = data.get("temperature")
            device_data["mode"] = data.get("mode")
            device_data["fan_speed"] = data.get("fan_speed")
            device_data["swing"] = data.get("swing")

        r.hset("devices", device_id, json.dumps(device_data))
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da mensagem: {e}")
    except Exception as e:
        print(f"Erro ao processar mensagem do tópico {topic}: {e}")

def consume_messages(topic, group_id):
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=["localhost:9092"],
            auto_offset_reset="latest",
            group_id=group_id
        )
        for message in consumer:
            process_message(message, topic)
    except Exception as e:
        print(f"Erro ao consumir mensagens do tópico {topic}: {e}")

def start_broker_listener():
    print("Consumidor iniciado! Aguardando mensagens...")
    discovery_thread = threading.Thread(target=consume_discovery_messages)
    discovery_thread.daemon = True
    discovery_thread.start()

    topics = {
        "temperature_data": ("temperature_consumer_group", consume_messages),
        "luminosity_data": ("luminosity_consumer_group", consume_messages)
    }

    threads = []
    for topic, (group_id, func) in topics.items():
        thread = threading.Thread(target=func, args=(topic, group_id))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()