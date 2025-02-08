import grpc
from actuators import lamp_service_pb2
from actuators import lamp_service_pb2_grpc

class LampClient:
    def __init__(self, host="localhost", port=50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = lamp_service_pb2_grpc.LampServiceStub(self.channel)  # Corrigido para LampServiceStub

    def ligar_lampada(self):
        request = lamp_service_pb2.Empty()  # Usando a classe Empty para o request
        response = self.stub.LigarLampada(request)
        return response  # Retorna a resposta (Empty)

    def desligar_lampada(self):
        request = lamp_service_pb2.Empty()  # Usando a classe Empty para o request
        response = self.stub.DesligarLampada(request)
        return response  # Retorna a resposta (Empty)

if __name__ == "__main__":
    client = LampClient()

    # Testando o controle da lâmpada
    print("Ligando a lâmpada...")
    client.ligar_lampada()  # Chama o método para ligar a lâmpada

    print("Desligando a lâmpada...")
    client.desligar_lampada()  # Chama o método para desligar a lâmpada