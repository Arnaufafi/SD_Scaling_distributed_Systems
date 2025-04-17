import xmlrpc.client
import threading
import time
import random

# Configuración
ALL_SERVER_URLS = [
    'http://localhost:8000',
    'http://localhost:8001',
    'http://localhost:8002'
]

OBSERVER_URLS = [
    'http://localhost:8010',
    'http://localhost:8011',
]

NUM_CLIENTES = 500
fake_insults = [f"insult_{i}" for i in range(100)]
sample_texts = [
    "Ets un TAP DE BASSA i un GAMARÚS!",
    "Cap de suro, què fas?",
    "AIXAFAGUITARRES total",
    "Simplement insult_42 i insult_13",
    "Tot correcte, res d'insults aquí"
]

def simulated_client(index, server_url):
    try:
        proxy = xmlrpc.client.ServerProxy(server_url)

        # Añadir insulto
        insult = random.choice(fake_insults)
        proxy.add_insults(insult)

        # Enviar texto aleatorio con insultos
        text = random.choice(sample_texts) + f" {insult}"
        proxy.enviar_texto(text)

        # Obtener resultados filtrados
        filtered = proxy.get_filtered()
        print(f"[Cliente {index}] ({server_url}) Último resultado filtrado: {filtered[-1] if filtered else 'Vacío'}")

    except Exception as e:
        print(f"[Cliente {index}] Error: {e}")

def stress_test(n_nodes):
    print(f"\n=== Iniciando test con {n_nodes} nodo(s) ===")
    server_urls = ALL_SERVER_URLS[:n_nodes]

    # Suscribir observadores al nodo principal
    main = xmlrpc.client.ServerProxy(server_urls[0])
    for url in OBSERVER_URLS:
        try:
            main.subscribe(url.split('//')[1])
        except:
            pass

    # Suscribir nodos entre sí
    for url in server_urls[1:]:
        try:
            main.subscribeServer(url.split('//')[1])
        except:
            pass

    threads = []
    start = time.time()

    # Lanzar clientes distribuidos
    for i in range(NUM_CLIENTES):
        server_url = random.choice(server_urls)
        t = threading.Thread(target=simulated_client, args=(i, server_url))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end = time.time()
    duration = end - start
    print(f"Tiempo con {n_nodes} nodo(s): {duration:.2f} segundos")
    return duration

# Ejecutar tests con 1, 2 y 3 nodos
tiempos = []
for n in [1, 2, 3]:
    tiempo = stress_test(n)
    tiempos.append(tiempo)

print(tiempos)
