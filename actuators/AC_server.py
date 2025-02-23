import grpc
from concurrent import futures
import time
from kafka import KafkaProducer
import AC_service_pb2
import AC_service_pb2_grpc
import json

# Configuração do tópico de comandos
COMMAND_TOPIC = "temperature_commands"
BROKER_URL = "localhost:9092"
producer = KafkaProducer(bootstrap_servers=BROKER_URL,
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))

# Implementação do serviço
class ACService(AC_service_pb2_grpc.AirConditionerServiceServicer):
    def __init__(self):
        self.status = AC_service_pb2.AirConditionerControl(
            device_id="AC_sensor", power=False, temperature=24, mode=AC_service_pb2.COOL,
            fan_speed=AC_service_pb2.MEDIUM, swing=False
        )

    def SetControl(self, request, context):
        # Atualiza o status do ar-condicionado
        self.status = request

        command = {
            "action": "set_all",
            "device_id": request.device_id,
            "temperature": request.temperature,
            "power": request.power,
            "mode": request.mode,
            "fan_speed": request.fan_speed,
            "swing": request.swing,
        }
        producer.send(COMMAND_TOPIC, command)

        '''
        # Publica o comando no tópico
        if request.temperature is not None:
            command = {"action": "set_temperature", "temperature": request.temperature}
            producer.send(COMMAND_TOPIC, command)
            print(f"[AC Server] Sent command: {command}")
        if request.power is not None:
            command = {"action": "set_power", "power": request.power}
            producer.send(COMMAND_TOPIC, command)
            print(f"[AC Server] Sent command: {command}")
        if request.mode is not None:
            command = {"action": "set_mode", "mode": request.mode}
            producer.send(COMMAND_TOPIC, command)
            print(f"[AC Server] Sent command: {command}")
        if request.fan_speed is not None:
            command = {"action": "set_fan_speed", "fan_speed": request.fan_speed}
            producer.send(COMMAND_TOPIC, command)
            print(f"[AC Server] Sent command: {command}")
        if request.swing is not None:
            command = {"action": "set_swing", "swing": request.swing}
            producer.send(COMMAND_TOPIC, command)
            print(f"[AC Server] Sent command: {command}")
        '''
        return AC_service_pb2.Response(message="Controle atualizado com sucesso!")

    def GetStatus(self, request, context):
        return self.status

# Função para iniciar o servidor
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    AC_service_pb2_grpc.add_AirConditionerServiceServicer_to_server(ACService(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    print("Servidor gRPC rodando na porta 50052...")
    try:
        while True:
            time.sleep(86400)  # Mantém o servidor rodando
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
