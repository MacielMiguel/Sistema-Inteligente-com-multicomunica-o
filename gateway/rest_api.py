from flask import Flask, jsonify, request
import redis
import json
import grpc_client as grpc

app = Flask(__name__)

# Configuração do Redis
redis_host = 'localhost'
redis_port = 6379
redis_db = 0
try:
    r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
except redis.exceptions.ConnectionError as e:
    print(f"Erro ao conectar ao Redis: {e}")

# Método para retornar os dados de um dispositivo
def get_device_data(device):
    try:
        device_data = r.hget("devices", device)
        if device_data:
            return json.loads(device_data.decode())
        return None
    except Exception as e:
        print(f"Erro ao obter dados do dispositivo {device}: {e}")
        return None

# Método para listar dispositivos
@app.route("/devices", methods=["GET"])
def list_devices():
    try:
        devices = r.hgetall("devices")
        devices = {k.decode(): json.loads(v.decode()) for k, v in devices.items()}
        return jsonify(devices)
    except Exception as e:
        print(f"Erro ao listar dispositivos: {e}")
        return jsonify({"error": "Erro ao listar dispositivos"}), 500
    
# Método para listar um dispositivo somente
@app.route("/devices/<device>", methods=["GET"])
def get_device_info(device):
    device_data = get_device_data(device)
    if device_data:
        return jsonify({device: device_data})
    return jsonify({"error": "Dispositivo não encontrado"}), 404

# Método para lista estado de um dispositivo
@app.route("/devices/<device>/status", methods=["GET"])
def get_status(device):
    device_data = get_device_data(device)
    if device_data:
        return jsonify({device: device_data.get("status")})
    return jsonify({"error": "Dispositivo não encontrado"}), 404

# Método para togglar um dispositivo
@app.route("/devices/<device>/toggle", methods=["POST"])
def toggle_device(device):
    device_data = get_device_data(device)
    try:
        if device_data:
            # Tratamento no gRPC
            if device_data["type"] == "luminosity":
                lamp_client = grpc.LampClient()
                if device_data["status"] == "off":
                    lamp_client.ligar_lampada()
                else:
                    lamp_client.desligar_lampada()
            elif device_data["type"] == "AC":
                ac_client = grpc.ACClient()
                # Mantém informações do dispositivo
                temperature = int(device_data.get("temperature"))
                mode = device_data.get("mode")
                fan_speed = device_data.get("fan_speed")
                swing = (device_data.get("swing") == "True")
                # Troca a informação de status dele
                ac_client.set_control(device_id=device, power=device_data["status"] == "off", temperature=temperature, mode=mode, fan_speed=fan_speed, swing=swing)

            # Tratamento no redis
            device_data["status"] = "on" if device_data["status"] == "off" else "off"
            r.hset("devices", device, json.dumps(device_data))
            return jsonify({device: device_data["status"]})
    except Exception as e:
        print(f"Erro ao togglear dispositivo {device}: {e}")
    return jsonify({"error": "Dispositivo não encontrado"}), 404

# Método para deletar um dispositivo
@app.route("/devices/<device>", methods=["DELETE"])
def delete_device(device):
    try:
        device_data = get_device_data(device)
        if device_data:
            if device_data["type"] == "luminosity":
                lamp_client = grpc.LampClient()
                lamp_client.desligar_lampada()
            elif device_data["type"] == "AC":
                ac_client = grpc.ACClient()
                ac_client.set_control(device_id=device, power=False, temperature=int(device_data.get("temperature")), mode=device_data.get("mode"), fan_speed=device_data.get("fan_speed"), swing=device_data.get("swing") == "True")
            r.hdel("devices", device)
            return jsonify({"message": f"Dispositivo {device} deletado com sucesso"})
        return jsonify({"error": "Dispositivo não encontrado"}), 404
    except Exception as e:
        print(f"Erro ao deletar dispositivo {device}: {e}")
        return jsonify({"error": "Erro ao deletar dispositivo"}), 500

# Método para editar um dispositivo
@app.route("/devices/<device>", methods=["PUT"])
def edit_device(device):
    device_data = r.hget("devices", device)
    if device_data:
        device_data = json.loads(device_data.decode())
        try:
            new_data = request.get_json()

            # Atualiza as informações do dispositivo com os dados recebidos
            device_data.update(new_data)
            r.hset("devices", device, json.dumps(device_data))

            if device_data["type"] == "AC":
                ac_client = grpc.ACClient()
                ac_client.set_control(device_id=device, power=device_data["status"] == "on", temperature=device_data["temperature"], mode=device_data["mode"], fan_speed=device_data["fan_speed"], swing=device_data["swing"] == "True")
            return jsonify({"message": f"Dispositivo {device} atualizado com sucesso"})
        except (ValueError, TypeError) as e:
            return jsonify({"error": f"Erro ao atualizar dispositivo: {e}"}), 400 # Retorna erro se os dados forem inválidos
    return jsonify({"error": "Dispositivo não encontrado"}), 404

def start_rest_server():
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
