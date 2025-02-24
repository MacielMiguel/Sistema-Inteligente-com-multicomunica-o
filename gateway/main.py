import threading
from rest_api import start_rest_server
from broker_consumer import start_broker_listener

if __name__ == "__main__":
    rest_thread = threading.Thread(target=start_rest_server)
    rest_thread.start()

    broker_thread = threading.Thread(target=start_broker_listener)
    broker_thread.start()

    print("Gateway iniciado!")