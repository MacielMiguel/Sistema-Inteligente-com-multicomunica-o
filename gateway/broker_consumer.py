from kafka import KafkaConsumer
import redis
import threading
import json

# Configuração do Redis
redis_host = 'localhost'
redis_port = 6379
redis_db = 0
r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

def callback(message):
    print(f"📥 Mensagem recebida do sensor: {message.value.decode()}")
    data = json.loads(message.value.decode())
    device_id = data.get("device_id")
    status = data.get("status")
    
    # Verifica se o dispositivo já existe no Redis
    existe = r.hexists("devices", device_id)  # True ou False

    if not existe:
        try:
            # Armazena o dispositivo no Redis
            r.hset("devices", device_id, json.dumps({"status": status}))
        except (redis.exceptions.ConnectionError, redis.exceptions.ResponseError) as e:
            print(f"Erro ao adicionar dispositivo ao Redis: {e}")
        except TypeError as e:
            print(f"Erro ao codificar dados para JSON: {e}")
    elif existe and status != r.hget("devices", device_id).decode():
        try:
            # Atualiza o status do dispositivo no Redis
            r.hset("devices", device_id, json.dumps({"status": status}))
        except (redis.exceptions.ConnectionError, redis.exceptions.ResponseError) as e:
            print(f"Erro ao atualizar dispositivo no Redis: {e}")
        except TypeError as e:
            print(f"Erro ao codificar dados para JSON: {e}")
    
def start_consumer_AC():
    consumer_AC = KafkaConsumer(
        "temperature_data",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="latest"
    )
    for message in consumer_AC:
        if message.topic == "temperature_data":
            callback(message)

def start_consumer_gates():
    consumer_gates = KafkaConsumer(
        "gates_data",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="latest"
    )
    for message in consumer_gates:
        if message.topic == "gates_data":
            callback(message)

def start_consumer_luminosity():
    consumer_luminosity = KafkaConsumer(
        "luminosity_data",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="latest"
    )
    for message in consumer_luminosity:
        if message.topic == "luminosity_data":
            callback(message)

def start_broker_listener():
    print("Consumidor iniciado! Aguardando mensagens...")

    # Therad para consumir mensagens dos portões
    AC_thread = threading.Thread(target=start_consumer_AC)
    AC_thread.start()

    # Therad para consumir mensagens dos portões
    gates_thread = threading.Thread(target=start_consumer_gates)
    gates_thread.start()
    
    # Thread para consumir mensagens das lâmpadas
    luminosity_thread = threading.Thread(target=start_consumer_luminosity)
    luminosity_thread.start()