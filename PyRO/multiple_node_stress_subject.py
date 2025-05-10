import Pyro4
import threading
import time
import random
import matplotlib.pyplot as plt

NUM_CLIENTS = 200
SERVER_NAMES = ["server1.observable", "server2.observable", "server3.observable"]

fake_insults = [f"insult_{i}" for i in range(100)]
sample_texts = [
    "You're a TAP DE BASSA and a GAMARÚS!",
    "Blockhead, what are you doing?",
    "A total AIXAFAGUITARRES",
    "Simply insult_42 and insult_13",
    "All good, no insults here"
]

def simulated_client(index, server_name):
    try:
        ns = Pyro4.locateNS()
        proxy = Pyro4.Proxy(ns.lookup(server_name))

        insult = random.choice(fake_insults)
        if hasattr(proxy, "add_insults"):
            proxy.add_insults(insult)

        text = random.choice(sample_texts) + f" {insult}"
        proxy.send_text(text)

        filtered = proxy.get_filtered()
        print(f"[Client {index}] ({server_name}) Last filtered: {filtered[-1] if filtered else 'Empty'}")

    except Exception as e:
        print(f"[Client {index}] Error: {e}")


def stress_test(n_nodes):
    print(f"\n=== Starting test with {n_nodes} node(s) ===")
    server_names = SERVER_NAMES[:n_nodes]

    try:
        ns = Pyro4.locateNS()
        main_server = Pyro4.Proxy(ns.lookup(server_names[0]))

        for i, name in enumerate(server_names[1:], start=1):
            try:
                main_server.register_observer(server_names[0], server_names[i])
            except Exception as e:
                print(f"Could not connect server {name} to main: {e}")
    except Exception as e:
        print(f"Network setup error: {e}")
        return 0

    threads = []
    start = time.time()

    for i in range(NUM_CLIENTS):
        selected_server = server_names[i % len(server_names)]
        t = threading.Thread(target=simulated_client, args=(i, selected_server))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    duration = time.time() - start
    print(f"Time with {n_nodes} node(s): {duration:.2f} seconds")
    return duration

# === Run test with 1, 2, 3 nodes ===
if __name__ == "__main__":
    nodes = [1, 2, 3]
    times = [stress_test(n) for n in nodes]

    # Calculate speedups
    t1 = times[0]
    speedups = [t1 / t if t != 0 else 0 for t in times]

    # === Plots ===
    plt.figure(figsize=(12, 5))

    # Plot 1: Execution time
    plt.subplot(1, 2, 1)
    plt.plot(nodes, times, marker='o', color='blue')
    plt.title("Execution Time vs Nodes")
    plt.xlabel("Number of Nodes")
    plt.ylabel("Time (seconds)")
    plt.grid(True)

    # Plot 2: Speedup
    plt.subplot(1, 2, 2)
    plt.plot(nodes, speedups, marker='o', color='green')
    plt.title("Speedup vs Nodes")
    plt.xlabel("Number of Nodes")
    plt.ylabel("Speedup (T1 / Tn)")
    plt.grid(True)

    plt.tight_layout()
    plt.show()
