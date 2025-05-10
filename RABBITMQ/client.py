import subprocess
import time
import pika
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt

# RabbitMQ configuration
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
queue_name = 'text_queue'
result_queue = 'RESULTS'

NUM_EXECUTIONS = 200
client_scripts = ["RABBITMQ/text_producer.py"] * NUM_EXECUTIONS + ["RABBITMQ/angry_producer.py"] * NUM_EXECUTIONS

def run_script(script):
    p = subprocess.Popen(["python3", script])
    p.wait()

def fill_queue():
    # Delete previous state of queues
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_delete(queue=queue_name)
    channel.queue_delete(queue=result_queue)
    connection.close()

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
        p = subprocess.Popen(["python3", "RABBITMQ/server.py"])
        server_processes.append(p)

    # Wait for them to finish
    for p in server_processes:
        p.wait()

    end_time = time.time()
    elapsed = end_time - start_time 
    print(f"[server] {n} server(s) finished in {elapsed:.2f} seconds.")
    return elapsed

# Dictionary of times
times = {}

# Run tests with 1, 2 and 3 servers
for n_servers in [1, 2, 3]:
    fill_queue()
    elapsed_time = run_servers(n_servers)
    times[n_servers] = elapsed_time

# Show results
print("\n[results] Time and speed-up:")
baseline = times[1]
for n in [1, 2, 3]:
    speedup = baseline / times[n]
    print(f"  {n} server(s): {times[n]:.2f} sec | speed-up: {speedup:.2f}x")

nodes = [1, 2, 3]
times_list = [times[n] for n in nodes]
speedups = [baseline / times[n] for n in nodes]
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(nodes, times_list, marker='o', color='blue')
plt.title("Execution Time vs Nodes (RabbitMQ)")
plt.xlabel("Number of nodes")
plt.ylabel("Time (seconds)")
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(nodes, speedups, marker='o', color='green')
plt.title("Speedup vs Nodes (RabbitMQ)")
plt.xlabel("Number of nodes")
plt.ylabel("Speedup (T1 / Tn)")
plt.grid(True)

plt.tight_layout()
plt.show()
