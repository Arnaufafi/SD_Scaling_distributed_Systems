import Pyro4
import threading
import time
import random

# Nombre Pyro del servidor (ajusta según tu setup)
PYRO_SERVER_NAME = "server1.observable"
NUM_CLIENTES = 500

# Insultos y textos de ejemplo
fake_insults = [f"insult_{i}" for i in range(100)]
sample_texts = [
    "Ets un TAP DE BASSA i un GAMARÚS!",
    "Cap de suro, què fas?",
    "AIXAFAGUITARRES total",
    "Simplement insult_42 i insult_13",
    "Tot correcte, res d'insults aquí"
]

# Simula un cliente Pyro
def simulated_client(index):
    try:
        ns = Pyro4.locateNS()
        proxy = Pyro4.Proxy(ns.lookup(PYRO_SERVER_NAME))

        # Añadir insulto (si tu servidor tiene ese método)
        insult = random.choice(fake_insults)
        if hasattr(proxy, "add_insults"):
            proxy.add_insults(insult)

        # Enviar texto para censura
        text = random.choice(sample_texts) + f" {insult}"
        proxy.enviar_texto(text)

        # Obtener resultados filtrados
        filtered = proxy.get_filtered()
        print(f"[Cliente {index}] Último filtrado: {filtered[-1] if filtered else 'Vacío'}")

    except Exception as e:
        print(f"[Cliente {index}] Error: {e}")

# Ejecutar el test
def main():
    start_time = time.time()

    threads = []
    for i in range(NUM_CLIENTES):
        t = threading.Thread(target=simulated_client, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    end_time = time.time()
    print(f"Test completado con {NUM_CLIENTES} clientes en {end_time - start_time:.2f} segundos.")

if __name__ == "__main__":
    main()
