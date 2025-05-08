import subprocess
import time
import pika
import requests
import math
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt

# Configuración
QUEUE_NAME = 'text_queue'
RESULT_QUEUE = 'RESULTS'
RABBIT_API_URL = 'http://localhost:15672/api/queues/%2F/text_queue'
USERNAME = 'guest'
PASSWORD = 'guest'
LOAD_PER_WORKER = 25  # C: capacidad de un worker

NUM_EXECUTIONS = 200
client_scripts = (
    ["RABBITMQ/text_producer.py"] * NUM_EXECUTIONS +
    ["RABBITMQ/angry_producer.py"] * NUM_EXECUTIONS +
    ["RABBITMQ/insult_producer.py"] * 50
)

def get_L():
    try:
        res = requests.get(RABBIT_API_URL, auth=(USERNAME, PASSWORD)).json()
        return int(res['messages_ready'])  # mensajes listos para ser procesados
    except Exception as e:
        print(f"[Error] No se pudo obtener L: {e}")
        return 0

def estimate_T():
    # Simulación de tiempo medio por mensaje, ajusta si lo conoces mejor
    return 1.0  # segundos por mensaje (puedes estimarlo dinámicamente si tienes logs)

def calculate_workers(L, T):
    N = (L * T) / LOAD_PER_WORKER
    return max(1, math.ceil(N))

def run_script(script):
    p = subprocess.Popen(["python3", script])
    p.wait()

def fill_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_delete(queue=QUEUE_NAME)
    channel.queue_delete(queue=RESULT_QUEUE)
    connection.close()

    print("[client] Llenando la cola con tareas...")
    with ThreadPoolExecutor(max_workers=1000) as executor:
        executor.map(run_script, client_scripts)
    print("[client] Cola llena.")

def run_dynamic_servers():
    L = get_L()
    T = estimate_T()
    workers = calculate_workers(L, T)
    print(f"[server] Carga detectada: L={L}, T={T:.2f} -> lanzando {workers} workers.")

    server_processes = []
    start_time = time.time()

    for _ in range(workers):
        p = subprocess.Popen(["python3", "RABBITMQ/server1.py"])
        server_processes.append(p)

    for p in server_processes:
        p.wait()

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"[server] {workers} server(s) finished in {elapsed:.2f} seconds.")
    return workers, elapsed

# Ejecutar prueba con escalado dinámico
fill_queue()
start = time.time()
workers_used, elapsed_time = run_dynamic_servers()
end = time.time()

# Mostrar resultados
print("\n[results] Dynamic Scaling:")
print(f"  Workers usados: {workers_used}")
print(f"  Tiempo total: {elapsed_time:.2f} segundos")

# Gráfico
plt.figure(figsize=(6, 4))
plt.bar(["Ejecución dinámica"], [elapsed_time], color='blue')
plt.title("Tiempo de ejecución con escalado dinámico")
plt.ylabel("Tiempo (segundos)")
plt.tight_layout()
plt.show()
