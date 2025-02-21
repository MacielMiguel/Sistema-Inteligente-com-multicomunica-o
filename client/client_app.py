import requests 

API_URL = "http://localhost:5000"

def list_devices():
    response = requests.get(f"{API_URL}/devices")
    print(response.json())

def toggle_device(device):
    response = requests.post(f"{API_URL}/devices/{device}/toggle")
    print(response.json())

def delete_device(device):
    response = requests.delete(f"{API_URL}/devices/{device}")
    print(response.json())

if __name__ == "__main__":
    while(True):
        print("1. Listar dispositivos")
        print("2. Toggle no dispositivo desejado")
        print("3. Deletar dispositivo desejado")
        print("exit. Sair")
        
        choice = input("Escolha uma opção: ")
        
        if choice == "1":
            list_devices()
        elif choice == "2":
            device = input("Nome do dispositivo: ")
            toggle_device(device)
        elif choice == "3":
            device = input("Nome do dispositivo: ")
            delete_device()
        elif choice == "exit":
            break