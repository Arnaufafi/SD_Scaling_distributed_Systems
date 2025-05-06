import subprocess
import time
import redis
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt

# Redis config
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
queue_name = "work_queue"
result_name = "result_list"
censor_list = "insults_list"

NUM_EXECUTIONS = 200
client_scripts = ["REDIS/text_producer.py"] * NUM_EXECUTIONS + ["REDIS/angry_producer.py"] * NUM_EXECUTIONS

def run_script(script):
    subprocess.run(["python3", script])
    time.sleep(0.01)

def fill_queue():
    # Clean Redis state
    client.delete(queue_name)
    client.delete(result_name)

    # Reload insults
    subprocess.run(["python3", "REDIS/insult_producer.py"])
    subprocess.run(["python3", "REDIS/insult_consumer.py"])

    print("[client] Filling the queue with tasks...")
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=1000) as executor:
        executor.map(run_script, client_scripts)
    end_time = time.time()
    print(f"[client] Queue filled in {end_time - start_time:.2f} seconds.")

def run_servers(n):
    print(f"[server] Running {n} server(s)...")
    server_processes = []
    start_time = time.time()

    for _ in range(n):
        p = subprocess.Popen(["python3", "REDIS/server1.py"])
        server_processes.append(p)

    # Wait for all servers to finish
    for p in server_processes:
        p.wait()

    end_time = time.time()
    elapsed = end_time - start_time - 1  # -1s compensation for startup delay
    print(f"[server] {n} server(s) finished in {elapsed:.2f} seconds.")
    return elapsed

# Dictionary to store times
times = {}

# Run tests for 1, 2 and 3 server instances
for n_servers in [1, 2, 3]:
    fill_queue()
    elapsed_time = run_servers(n_servers)
    times[n_servers] = elapsed_time

# Calculate speed-up
print("\n[results] Time and speed-up:")
baseline = times[1]
for n in [1, 2, 3]:
    speedup = baseline / times[n]
    print(f"  {n} server(s): {times[n]:.2f} sec | speed-up: {speedup:.2f}x")

nodos = [1, 2, 3]
tiempos = [times[n] for n in nodos]
speedups = [baseline / times[n] for n in nodos]
plt.figure(figsize=(12, 5))

# Gráfico 1: Tiempo de ejecución
plt.subplot(1, 2, 1)
plt.plot(nodos, tiempos, marker='o', color='blue')
plt.title("Tiempo de ejecución vs Nodos")
plt.xlabel("Número de nodos")
plt.ylabel("Tiempo (segundos)")
plt.grid(True)

# Gráfico 2: Speedup
plt.subplot(1, 2, 2)
plt.plot(nodos, speedups, marker='o', color='green')
plt.title("Speedup vs Nodos")
plt.xlabel("Número de nodos")
plt.ylabel("Speedup (T1 / Tn)")
plt.grid(True)

plt.tight_layout()
plt.show()
