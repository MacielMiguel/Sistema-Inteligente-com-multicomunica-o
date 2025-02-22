from flask import Flask, jsonify, request
import redis
import json

app = Flask(__name__)

# Configuração do Redis
redis_host = 'localhost'
redis_port = 6379
redis_db = 0
r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

# Método para listar dispositivos
@app.route("/devices", methods=["GET"])
def list_devices():
    devices = r.hgetall("devices")
    devices = {k.decode(): json.loads(v.decode()) for k, v in devices.items()}
    return jsonify(devices)

# Método para lista estado de um dispositivo
@app.route("/devices/<device>/status", methods=["GET"])
def get_status(device):
    device_data = r.hget("devices", device)
    if device_data:
        return jsonify({device: json.loads(device_data.decode())})
    return jsonify({"error": "Dispositivo não encontrado"}), 404

# Método para togglar um dispositivo
@app.route("/devices/<device>/toggle", methods=["POST"])
def toggle_device(device):
    device_data = r.hget("devices", device)
    if device_data:
        device_data = json.loads(device_data.decode())
        device_data["status"] = "on" if device_data["status"] == "off" else "off"
        r.hset("devices", device, json.dumps(device_data))
        return jsonify({device: device_data["status"]})
    return jsonify({"error": "Dispositivo não encontrado"}), 404

# Método para deletar um dispositivo
@app.route("/devices/<device>", methods=["DELETE"])
def delete_device(device):
    if r.hdel("devices", device):
        return jsonify({"message": f"Dispositivo {device} deletado com sucesso"})
    return jsonify({"error": "Dispositivo não encontrado"}), 404

def start_rest_server():
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
