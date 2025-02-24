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

    def ligar_lampada(self, device_id):
        request = lamp_service_pb2.LigarLampadaRequest(device_id=device_id)
        response = self.stub.LigarLampada(request)
        return response

    def desligar_lampada(self, device_id):
        request = lamp_service_pb2.LigarLampadaRequest(device_id=device_id)
        response = self.stub.DesligarLampada(request)
        return response

    '''def MudarCorLampada(self, device_id="luminosity", status="on", color='WHITE'):
        self.estado = "ligada"
        control = {
            "action": "mudar_cor",
            "device_id": device_id,
            "type": "luminosity",
            "status": status,
            "color": color
        }
        response = self.stub.MudarCorLampada(control)
        return response'''

class ACClient:
    def __init__(self, host="localhost", port=50052):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = AC_service_pb2_grpc.AirConditionerServiceStub(self.channel)

    def set_control(self, device_id="AC", power=True, temperature=22, mode="COOL", fan_speed="MEDIUM", swing=False):
        control = AC_service_pb2.AirConditionerControl(
            device_id=device_id,
            power=power,
            temperature=temperature,
            mode=getattr(AC_service_pb2, mode),
            fan_speed=getattr(AC_service_pb2, fan_speed),
            swing=swing
        )
        response = self.stub.SetControl(control)
        return response

    def get_status(self):
        request = Empty() 
        ac_status = self.stub.GetStatus(request) 
        print(ac_status)