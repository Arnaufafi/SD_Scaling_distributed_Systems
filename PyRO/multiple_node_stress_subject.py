import Pyro4
import threading
import time
import random


NUM_CLIENTES = 500
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
        selected_server = random.choice(server_names)
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
    tiempos = []
    for n in [1, 2, 3]:
        tiempo = stress_test(n)
        tiempos.append(tiempo)
    print(f"\nResultados: {tiempos}")
