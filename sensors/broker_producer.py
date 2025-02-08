from kafka import KafkaProducer, KafkaConsumer

BROKER_URL = "localhost:9092"  # Kafka Broker URL

def get_broker_connection():
    """Retorna um produtor Kafka"""
    return KafkaProducer(bootstrap_servers=[BROKER_URL])

def get_broker_consumer(topic):
    """Retorna um consumidor Kafka para um tópico"""
    return KafkaConsumer(topic, bootstrap_servers=[BROKER_URL], auto_offset_reset="earliest")
