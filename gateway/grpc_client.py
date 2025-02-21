import grpc
import actuators as act

'''
from actuators import lamp_service_pb2
from actuators import lamp_service_pb2_grpc
from actuators import AC_service_pb2
from actuators import AC_service_pb2_grpc
'''

def run():
    # Canal para o servidor (substitua com o endereço do seu servidor)
    with grpc.insecure_channel('localhost:50051') as channel:
        # Stub para o serviço
        stub = act.AC_service_pb2_grpc.AirConditionerServiceStub(channel)

        # Criando a mensagem de controle
        control = act.AC_service_pb2.AirConditionerControl(
            device_id="AC12345",
            power=True,
            temperature=22,
            mode=act.AC_service_pb2.COOL,
            fan_speed=act.AC_service_pb2.MEDIUM,
            swing=False
        )

        # Chamando o método SetControl
        response = stub.SetControl(control)
        print("Resposta do servidor:", response.message)

        # Chamando o método GetStatus
        status = stub.GetStatus(act.AC_service_pb2.AirConditionerControl())
        print("Status do ar-condicionado:")
        print(status)

class LampClient:
    def __init__(self, host="localhost", port=50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = act.lamp_service_pb2_grpc.LampServiceStub(self.channel)  # Corrigido para LampServiceStub

    def ligar_lampada(self):
        request = act.lamp_service_pb2.Empty()  # Usando a classe Empty para o request
        response = self.stub.LigarLampada(request)
        return response  # Retorna a resposta (Empty)

    def desligar_lampada(self):
        request = act.lamp_service_pb2.Empty()  # Usando a classe Empty para o request
        response = self.stub.DesligarLampada(request)
        return response  # Retorna a resposta (Empty)

if __name__ == "__main__":
    run()
    client = LampClient()

    # Testando o controle da lâmpada
    print("Ligando a lâmpada...")
    client.ligar_lampada()  # Chama o método para ligar a lâmpada

    print("Desligando a lâmpada...")
    client.desligar_lampada()  # Chama o método para desligar a lâmpada

