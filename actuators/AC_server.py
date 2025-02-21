import grpc
from concurrent import futures
import time

import AC_service_pb2
import AC_service_pb2_grpc

# Implementação do serviço
class ACService(AC_service_pb2_grpc.AirConditionerServiceServicer):
    def __init__(self):
        self.status = AC_service_pb2.AirConditionerControl(
            device_id="AC12345", power=False, temperature=24, mode=AC_service_pb2.COOL,
            fan_speed=AC_service_pb2.MEDIUM, swing=False
        )

    def SetControl(self, request, context):
        # Atualiza o status do ar-condicionado
        self.status = request
        return AC_service_pb2.Response(message="✅ Controle atualizado com sucesso!")

    def GetStatus(self, request, context):
        return self.status

# Função para iniciar o servidor
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    AC_service_pb2_grpc.add_AirConditionerServiceServicer_to_server(ACService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Servidor gRPC rodando na porta 50051...")
    try:
        while True:
            time.sleep(86400)  # Mantém o servidor rodando
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
