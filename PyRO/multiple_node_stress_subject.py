import Pyro4
import threading
import time
import random
import matplotlib.pyplot as plt


NUM_CLIENTES = 200
SERVER_NAMES = ["server1.observable", "server2.observable", "server3.observable"]

fake_insults = [f"insult_{i}" for i in range(100)]
sample_texts = [
    "Ets un TAP DE BASSA i un GAMARÚS!",
    "Cap de suro, què fas?",
    "AIXAFAGUITARRES total",
    "Simplement insult_42 i insult_13",
    "Tot correcte, res d'insults aquí"
]

def simulated_client(index, server_name):
    try:
        ns = Pyro4.locateNS()
        proxy = Pyro4.Proxy(ns.lookup(server_name))

        insult = random.choice(fake_insults)
        if hasattr(proxy, "add_insults"):
            proxy.add_insults(insult)

        text = random.choice(sample_texts) + f" {insult}"
        proxy.enviar_texto(text)

        filtered = proxy.get_filtered()
        print(f"[Cliente {index}] ({server_name}) Último filtrado: {filtered[-1] if filtered else 'Vacío'}")

    except Exception as e:
        print(f"[Cliente {index}] Error: {e}")


def stress_test(n_nodes):
    print(f"\n=== Iniciando test con {n_nodes} nodo(s) ===")
    server_names = SERVER_NAMES[:n_nodes]

    try:
        ns = Pyro4.locateNS()
        main_server = Pyro4.Proxy(ns.lookup(server_names[0]))

        for i, name in enumerate(server_names[1:], start=1):
            try:
                main_server.register_observer(server_names[0], server_names[i])
            except Exception as e:
                print(f"No se pudo conectar servidor {name} al principal: {e}")
    except Exception as e:
        print(f"Error en la configuración de red: {e}")
        return 0

    threads = []
    start = time.time()

    for i in range(NUM_CLIENTES):
        selected_server = server_names[i % len(server_names)]
        t = threading.Thread(target=simulated_client, args=(i, selected_server))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    duration = time.time() - start
    print(f"Tiempo con {n_nodes} nodo(s): {duration:.2f} segundos")
    return duration

# === Ejecutar test con 1, 2, 3 nodos ===
if __name__ == "__main__":
    nodos = [1, 2, 3]
    tiempos = [stress_test(n) for n in nodos]

    # Calcular speedups
    t1 = tiempos[0]
    speedups = [t1 / t if t != 0 else 0 for t in tiempos]

    # === Gráficos ===
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

