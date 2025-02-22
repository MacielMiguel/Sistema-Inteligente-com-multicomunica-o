from kafka import KafkaConsumer
import redis
import threading
import json

# Configuração do Redis
redis_host = 'localhost'
redis_port = 6379
redis_db = 0
try:
    r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
except redis.exceptions.ConnectionError as e:
    print(f"Erro ao conectar ao Redis: {e}")

# Função para processar mensagens e criar os dispositivos no Redis
def process_message(message, topic):
    try:
        print(f"Mensagem recebida do tópico {topic}: {message.value.decode()}")
        data = json.loads(message.value.decode())
        device_id = data.get("device_id")
        status = data.get("status")
        device_type = data.get("type")
        temperature = data.get("temperature") if device_type == "AC" else None

        device_data = {"status": status, "type": device_type}
        if temperature:
            device_data["temperature"] = temperature

        r.hset("devices", device_id, json.dumps(device_data))
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da mensagem: {e}")
    except Exception as e:
        print(f"Erro ao processar mensagem do tópico {topic}: {e}")

# Função para consumir as mensagens dos tópicos Kafka
def consume_messages(topic):
    """Consome mensagens de um tópico Kafka."""
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=["localhost:9092"],
            auto_offset_reset="latest"
        )
        for message in consumer:
            process_message(message, topic)
    except Exception as e:
        print(f"Erro ao consumir mensagens do tópico {topic}: {e}")

def start_broker_listener():
    print("Consumidor iniciado! Aguardando mensagens...")

    topics = {
        "temperature_data": consume_messages,
        "gates_data": consume_messages,
        "luminosity_data": consume_messages
    }

    threads = []
    for topic, func in topics.items():
        thread = threading.Thread(target=func, args=(topic,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()