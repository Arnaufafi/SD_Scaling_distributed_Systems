import xmlrpc.client
import threading
import time
import random

# Servidores de Insultos 
server_urls = [
    'http://localhost:8000',     
]

#Observers
observer_urls = [
    'http://localhost:8010',  
    'http://localhost:8011',    
]

# Conectar al servidor de insultos en el puerto 8000
s = xmlrpc.client.ServerProxy(server_urls[0])

print(s.system.listMethods())

# Suscribir los observadores (8010 y 8011) al servidor de insultos (8000)
for url in observer_urls[0:]:
    try:
        print(f"Suscribiendo a {url}...")
        s.subscribe(url.split('//')[0])  
    except Exception as e:
        print(f"No se pudo suscribir a {url}: {e}")

# Cantidad de clientes simulados
NUM_CLIENTES = 500

# Insultos y textos de ejemplo para usar
fake_insults = [f"insult_{i}" for i in range(100)]
sample_texts = [
    "Ets un TAP DE BASSA i un GAMARÚS!",
    "Cap de suro, què fas?",
    "AIXAFAGUITARRES total",
    "Simplement insult_42 i insult_13",
    "Tot correcte, res d'insults aquí"
]

# Función que simula un cliente usando el servidor
def simulated_client(index):
    proxy = xmlrpc.client.ServerProxy(server_urls[0])

    try:
        # Añadir insulto
        insult = random.choice(fake_insults)
        proxy.add_insults(insult)

        # Enviar texto aleatorio con insultos
        text = random.choice(sample_texts) + f" {insult}"
        proxy.enviar_texto(text)

        # Obtener resultados filtrados
        filtered = proxy.get_filtered()
        print(f"[Cliente {index}] Último resultado filtrado: {filtered[-1] if filtered else 'Vacío'}")

    except Exception as e:
        print(f"[Cliente {index}] Error: {e}")

# Medir tiempo
start_time = time.time()

# Crear y lanzar los hilos
threads = []
for i in range(NUM_CLIENTES):
    t = threading.Thread(target=simulated_client, args=(i,))
    threads.append(t)
    t.start()

# Esperar a que terminen todos
for t in threads:
    t.join()

end_time = time.time()
print(f"Test completado con {NUM_CLIENTES} clientes en {end_time - start_time:.2f} segundos.")

