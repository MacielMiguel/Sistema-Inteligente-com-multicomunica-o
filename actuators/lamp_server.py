import grpc
from concurrent import futures
import lamp_service_pb2_grpc as grpc_service
from lamp_service_pb2 import Empty

class LampService(grpc_service.LampServiceServicer):
    """Implementação do serviço gRPC para a lâmpada"""
    
    def __init__(self):
        self.estado = "desligada"

    def LigarLampada(self, request, context):
        self.estado = "ligada"
        print("[Atuador] Lâmpada ligada.")
        return Empty()

    def DesligarLampada(self, request, context):
        self.estado = "desligada"
        print("[Atuador] Lâmpada desligada.")
        return Empty()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_service.add_LampServiceServicer_to_server(LampService(), server)
    
    server.add_insecure_port("[::]:50051")
    server.start()
    print("[Atuador] Servidor gRPC rodando na porta 50051...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
