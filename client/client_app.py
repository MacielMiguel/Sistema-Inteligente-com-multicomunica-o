import requests

API_URL = "http://localhost:5000"

def list_devices():
    response = requests.get(f"{API_URL}/devices")
    print(response.json())

def toggle_device(device):
    response = requests.post(f"{API_URL}/devices/{device}/toggle")
    print(response.json())

if __name__ == "__main__":
    print("1. Listar dispositivos")
    print("2. Ligar/Desligar lâmpada")
    
    choice = input("Escolha uma opção: ")
    
    if choice == "1":
        list_devices()
    elif choice == "2":
        toggle_device("lamp")
