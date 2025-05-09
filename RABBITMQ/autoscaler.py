import subprocess
import time
import matplotlib.pyplot as plt
from threading import Thread
import requests
from requests.auth import HTTPBasicAuth

# Parámetros del sistema
C = 5        # Capacidad de cada nodo (mensajes concurrentes)
T = 0.5      # Tiempo medio por mensaje (en segundos)
CHECK_INTERVAL = 5  # Intervalo de comprobación (s)
MAX_NODES = 20
QUEUE_NAME = "text_queue"


# Seguimiento para gráfico
time_points = []
node_counts = []

# Procesos de nodos activos
active_nodes = []

def get_arrival_rate(queue_name='text_queue'):
    """Consulta la API REST de RabbitMQ para obtener L (mensajes/segundo)."""
    url = f'http://localhost:15672/api/queues/%2F/{queue_name}'
    auth = HTTPBasicAuth('guest', 'guest')

    try:
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        data = response.json()
        rate = data.get('messages_details', {}).get('rate', 0.0)
        return rate
    except Exception as e:
        print("Error al obtener arrival rate desde la API de RabbitMQ:", e)
        return 0.0

def launch_node():
    """Lanza un nuevo nodo insult_filter.py."""
    p = subprocess.Popen(["python3", "RABBITMQ/insult_filter.py"])
    active_nodes.append(p)

def kill_node():
    """Termina un nodo insult_filter.py."""
    if active_nodes:
        p = active_nodes.pop()
        p.terminate()

def scaler_loop():
    """Bucle principal del autoscaler."""
    start_time = time.time()
    L=1
    while True:
        
        N = int((L * T) / C)
        N = max(1, min(N, MAX_NODES))

        # Escalado hacia arriba
        while len(active_nodes) < N:
            launch_node()

        # Escalado hacia abajo
        while len(active_nodes) > N:
            kill_node()

        elapsed = round(time.time() - start_time, 1)
        time_points.append(elapsed)
        node_counts.append(len(active_nodes))

        print(f"[{elapsed}s] Llegada: {L:.2f} msg/s | Nodos activos: {len(active_nodes)}")

        L = get_arrival_rate(QUEUE_NAME)  # Mensajes por segundo
        time.sleep(CHECK_INTERVAL)

def show_graph():
    """Muestra el gráfico del número de nodos activos en el tiempo."""
    plt.plot(time_points, node_counts, marker='o')
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Nodos activos")
    plt.title("Escalado dinámico de insult_filter.py")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    try:
        p = subprocess.Popen(["python3", "RABBITMQ/dinamic_clients.py"])
        active_nodes.append(p)
        thread = Thread(target=scaler_loop)
        thread.start()
        thread.join()
    except KeyboardInterrupt:
        print("Terminando escalador...")

    for p in active_nodes:
        p.terminate()

    show_graph()
