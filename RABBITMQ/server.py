import subprocess

server_scripts = [
    "RABBITMQ/insult_consumer.py",
    "RABBITMQ/insult_filter.py",
]

processes = []

print("[server] Starting RabbitMQ server tasks...")

for script in server_scripts:
    print(f"[server] Running {script}...")
    p = subprocess.Popen(["python3", script])
    processes.append(p)

# Wait for all server scripts to finish
for p in processes:
    p.wait()

print("[server] All RabbitMQ server tasks completed.")