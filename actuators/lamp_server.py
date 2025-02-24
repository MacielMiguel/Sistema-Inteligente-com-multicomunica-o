import grpc, json
from concurrent import futures
import lamp_service_pb2_grpc as grpc_service
from lamp_service_pb2 import Empty
from kafka import KafkaProducer

# Configuração do tópico de comandos
COMMAND_TOPIC = "luminosity_commands"
BROKER_URL = "localhost:9092"
producer = KafkaProducer(bootstrap_servers=BROKER_URL,
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))

class LampService(grpc_service.LampServiceServicer):
    def __init__(self):
        self.estado = "desligada"

    def LigarLampada(self, request, context):
        self.estado = "ligada"
        device_id = request.device_id
        command = {
            "action": "ligar",
            "device_id": device_id
        }
        producer.send(COMMAND_TOPIC, command)
        return Empty()

    def DesligarLampada(self, request, context):
        self.estado = "desligada"
        device_id = request.device_id
        command = {
            "action": "desligar",
            "device_id": device_id
        }
        producer.send(COMMAND_TOPIC, command)
        return Empty()
    
    '''def MudarCorLampada(self, request, context):
        self.estado = request
        command = {
            "action": "mudar_cor",
            "device_id": request.device_id,
            "type": "luminosity",
            "status": request.status,
            "color": request.color
        }
        producer.send(COMMAND_TOPIC, command)
        return Empty()'''

def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_service.add_LampServiceServicer_to_server(LampService(), server)
    
    server.add_insecure_port("[::]:50051")
    server.start()
    print("[Atuador] Servidor gRPC rodando na porta 50051...")
    server.wait_for_termination()

if __name__ == "__main__":
    server()
