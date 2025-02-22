import grpc
from actuators import lamp_service_pb2_grpc
from actuators import lamp_service_pb2
from actuators import AC_service_pb2_grpc
from actuators import AC_service_pb2
from google.protobuf.empty_pb2 import Empty

class LampClient:
    def __init__(self, host="localhost", port=50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = lamp_service_pb2_grpc.LampServiceStub(self.channel)

    def ligar_lampada(self):
        request = lamp_service_pb2.Empty()
        response = self.stub.LigarLampada(request)
        return response

    def desligar_lampada(self):
        request = lamp_service_pb2.Empty()
        response = self.stub.DesligarLampada(request)
        return response

class ACClient:
    def __init__(self, host="localhost", port=50052):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = AC_service_pb2_grpc.AirConditionerServiceStub(self.channel)

    def set_control(self, power=True, temperature=22, mode="COOL", fan_speed="MEDIUM", swing=False):
        control = AC_service_pb2.AirConditionerControl(
            device_id="AC12345",
            power=power,
            temperature=temperature,
            mode=getattr(AC_service_pb2, mode),
            fan_speed=getattr(AC_service_pb2, fan_speed),
            swing=swing
        )
        response = self.stub.SetControl(control)
        return response

    def get_status(self):
        request = Empty()  # Criando uma requisição vazia
        ac_status = self.stub.GetStatus(request)  # Chamando o método GetStatus
        print(ac_status)

if __name__ == "__main__":
    lamp_client = LampClient()
    ac_client = ACClient()

    # Testando a lâmpada
    print("Ligando a lâmpada...")
    lamp_client.ligar_lampada()
    print("Desligando a lâmpada...")
    lamp_client.desligar_lampada()

    # Testando o ar-condicionado
    print("Ligando o AC no modo COOL...")
    ac_response = ac_client.set_control(power=True, temperature=22, mode="COOL", fan_speed="MEDIUM")
    print("Resposta do AC:", ac_response.message)

    print("Obtendo status do AC...")
    ac_status = ac_client.get_status()
    print("Status do AC:", ac_status)
