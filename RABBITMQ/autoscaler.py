import subprocess
import time
import matplotlib.pyplot as plt
from threading import Thread
import requests
from requests.auth import HTTPBasicAuth

# System parameters
C = 5        # Capacity of each node (concurrent messages)
T = 0.5      # Average time per message (in seconds)
CHECK_INTERVAL = 5  # Check interval (s)
MAX_NODES = 20
QUEUE_NAME = "text_queue"

# Tracking for graph
time_points = []
node_counts = []

# Active node processes
active_nodes = []

def get_arrival_rate(queue_name='text_queue'):
    """Queries the RabbitMQ REST API to get L (messages/second)."""
    url = f'http://localhost:15672/api/queues/%2F/{queue_name}'
    auth = HTTPBasicAuth('guest', 'guest')

    try:
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        data = response.json()
        rate = data.get('messages_details', {}).get('rate', 0.0)
        return rate
    except Exception as e:
        print("Error getting arrival rate from RabbitMQ API:", e)
        return 0.0

def launch_node():
    """Launches a new insult_filter.py node."""
    p = subprocess.Popen(["python3", "RABBITMQ/insult_filter.py"])
    active_nodes.append(p)

def kill_node():
    """Terminates an insult_filter.py node."""
    if active_nodes:
        p = active_nodes.pop()
        p.terminate()

def scaler_loop():
    """Main loop of the autoscaler."""
    start_time = time.time()
    L = 1
    while True:
        
        N = int((L * T) / C)
        N = max(1, min(N, MAX_NODES))

        # Scale up
        while len(active_nodes) < N:
            launch_node()

        # Scale down
        while len(active_nodes) > N:
            kill_node()

        elapsed = round(time.time() - start_time, 1)
        time_points.append(elapsed)
        node_counts.append(len(active_nodes))

        print(f"[{elapsed}s] Arrival: {L:.2f} msg/s | Active nodes: {len(active_nodes)}")

        L = get_arrival_rate(QUEUE_NAME)  # Messages per second
        time.sleep(CHECK_INTERVAL)

def show_graph():
    """Displays the graph of active nodes over time."""
    plt.plot(time_points, node_counts, marker='o')
    plt.xlabel("Time (s)")
    plt.ylabel("Active nodes")
    plt.title("Dynamic scaling with RabbitMQ")
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
        print("Terminating scaler...")

    for p in active_nodes:
        p.terminate()

    show_graph()
