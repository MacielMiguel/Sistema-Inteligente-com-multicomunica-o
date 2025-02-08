from flask import Flask, jsonify, request

app = Flask(__name__)

devices = {
    "lamp": {"status": "off"},
    "fan": {"status": "off"}
}

@app.route("/devices", methods=["GET"])
def list_devices():
    return jsonify(devices)

@app.route("/devices/<device>/status", methods=["GET"])
def get_status(device):
    return jsonify({device: devices.get(device, "Desconhecido")})

@app.route("/devices/<device>/toggle", methods=["POST"])
def toggle_device(device):
    if device in devices:
        devices[device]["status"] = "on" if devices[device]["status"] == "off" else "off"
        return jsonify({device: devices[device]["status"]})
    return jsonify({"error": "Dispositivo não encontrado"}), 404

def start_rest_server():
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
