from kafka import KafkaConsumer

def callback(message):
    print(f"📥 Mensagem recebida do sensor: {message.value.decode()}")

def start_broker_listener():
    consumer = KafkaConsumer(
        "luminosity_data",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest"
    )
    print("📡 Aguardando mensagens...")
    for message in consumer:
        callback(message)