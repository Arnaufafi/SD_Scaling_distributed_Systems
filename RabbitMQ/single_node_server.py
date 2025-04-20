import subprocess
import time

server_scripts = [
    "REDIS/insult_producer.py",
    "REDIS/insult_broadcaster.py",
    "REDIS/insult_filter.py"
]

processes = []

print("[server] Iniciando tareas del servidor...")

for script in server_scripts:
    print(f"[server] Ejecutando {script}...")
    p = subprocess.Popen(["python3", script])
    processes.append(p)


print("[server] Tareas del servidor finalizadas.")
