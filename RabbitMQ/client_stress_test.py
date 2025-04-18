import subprocess
import time

# Cada cliente lanzará estas tareas
client_scripts = [
    "RabbitMQ/insult_consumer.py",
    "RabbitMQ/insult_subscriber.py",
    "RabbitMQ/text_producer.py",
    "RabbitMQ/angry_producer.py"
]

# Número de clientes simultáneos
NUM_CLIENTS = 10

all_processes = []

print(f"[client] Lanzando {NUM_CLIENTS} clientes...")

for i in range(NUM_CLIENTS):
    print(f"[client {i}] Iniciando...")
    for script in client_scripts:
        p = subprocess.Popen(["python3", script])
        all_processes.append(p)

print("[client] Todos los clientes han terminado.")
