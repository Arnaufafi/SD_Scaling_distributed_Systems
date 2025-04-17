import subprocess
import time

server_scripts = [
    "RabbitMQ/insult_producer.py",
    "RabbitMQ/insult_broadcaster.py",
    "RabbitMQ/insult_filter.py"
]

processes = []

print("[server] Iniciando tareas del servidor...")

for script in server_scripts:
    print(f"[server] Ejecutando {script}...")
    p = subprocess.Popen(["python3", script])
    processes.append(p)
    time.sleep(1)  # Pausa ligera para evitar sobrecarga inicial

# Esperar a que terminen (opcional, puedes comentar si quieres que corra sin bloquear)
for p in processes:
    p.wait()

print("[server] Tareas del servidor finalizadas.")
