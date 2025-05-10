import xmlrpc.client
import threading
import time
import random
import matplotlib.pyplot as plt

# Configuration
ALL_SERVER_URLS = [
    'http://localhost:8000',
    'http://localhost:8001',
    'http://localhost:8002'
]

NUM_CLIENTS = 200
fake_insults = [f"insult_{i}" for i in range(100)]
sample_texts = [
    "You are a TAP DE BASSA and a GAMARÚS!",
    "Blockhead, what are you doing?",
    "A total AIXAFAGUITARRES",
    "Simply insult_42 and insult_13",
    "All good, no insults here"
]

def simulated_client(index, server_url):
    try:
        proxy = xmlrpc.client.ServerProxy(server_url)

        # Add insult
        insult = random.choice(fake_insults)
        proxy.add_insults(insult)

        # Send random text with insults
        text = random.choice(sample_texts) + f" {insult}"
        proxy.enviar_texto(text)

        # Get filtered results
        filtered = proxy.get_filtered()
        print(f"[Client {index}] ({server_url}) Last filtered result: {filtered[-1] if filtered else 'Empty'}")

    except Exception as e:
        print(f"[Client {index}] Error: {e}")

def stress_test(n_nodes):
    print(f"\n=== Starting test with {n_nodes} node(s) ===")
    server_urls = ALL_SERVER_URLS[:n_nodes]

    threads = []
    start = time.time()

    # Launch distributed clients
    for i in range(NUM_CLIENTS):
        server_url = random.choice(server_urls)
        t = threading.Thread(target=simulated_client, args=(i, server_url))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end = time.time()
    duration = end - start
    print(f"Time with {n_nodes} node(s): {duration:.2f} seconds")
    return duration

# Run tests with 1, 2, and 3 nodes
nodes = [1, 2, 3]
times = [stress_test(n) for n in nodes]

# Calculate speedups
t1 = times[0]
speedups = [t1 / t for t in times]

# === Charts ===
plt.figure(figsize=(12, 5))

# Execution time
plt.subplot(1, 2, 1)
plt.plot(nodes, times, marker='o', color='blue')
plt.title("Execution Time vs Nodes")
plt.xlabel("Number of Nodes")
plt.ylabel("Time (seconds)")
plt.grid(True)

# Speedup
plt.subplot(1, 2, 2)
plt.plot(nodes, speedups, marker='o', color='green')
plt.title("Speedup vs Nodes")
plt.xlabel("Number of Nodes")
plt.ylabel("Speedup (T1 / Tn)")
plt.grid(True)

plt.tight_layout()
plt.show()
