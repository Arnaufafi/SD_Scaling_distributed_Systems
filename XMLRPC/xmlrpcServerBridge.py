from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import random
import xmlrpc.client
import threading
import time
import queue
import subprocess
from collections import deque

# Configuraciones del sistema
T = 0.5  # tiempo promedio por mensaje (en segundos)

# Ratio actual de mensajes por segundo (simulado o reportado por clientes)
current_L = 0

procesamiento_tiempos = deque(maxlen=100)
mensaje_timestamps = deque(maxlen=1000)

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Lista de insultos
insult_list = ["Nyicris", "Cap de suro", "Estaquirot", "AIXAFAGUITARRES", "BRÈTOL", "CURT DE GAMBALS", "TANOCA", "TÒTIL", "GAMARÚS", "TAP DE BASSA", "CAGABANDÚRRIES", "Mosqueta morta", "Mort de gana", "POCA-SOLTA", "BANDARRA"]
observers = []
serverObservers = []
ownURL = 'localhost:8000'

# Cola de trabajo y resultados filtrados
work_queue = queue.Queue()
filtered_results = []

# Parámetros de escalado
LOAD_PER_WORKER = 25
WORKER_SCRIPT = "XMLRPC/xmlrpcServerDinamic.py"
worker_processes = []

# Distribuir tareas a workers
def distribuir_trabajo():
    while True:
        texto = work_queue.get()
        if worker_processes:
            observer_url = random.choice(worker_processes)
            try:
                print(f"f'http://{observer_url}/RPC2'")
                proxy = xmlrpc.client.ServerProxy(f'http://{observer_url}/RPC2')
                inicio = time.time()
                resultado = proxy.censurar_insultos(texto)
                fin =time.time()
                procesamiento_tiempos.append(fin - inicio)
                filtered_results.append(resultado)
                print(f"[Trabajo] Texto censurado por {observer_url}: {resultado}")
            except Exception as e:
                print(f"[Error] Enviando a {observer_url}: {e}")
        else:
            print("[Aviso] No hay servidores disponibles para procesar texto.")
        work_queue.task_done()
        time.sleep(0.2)

def calcular_T():
    if not procesamiento_tiempos:
        return T  # fallback si aún no hay datos
    return (sum(procesamiento_tiempos) / len(procesamiento_tiempos))+1

def calcular_L():
    ahora = time.time()
    ventana = 5  # segundos
    recientes = [ts for ts in mensaje_timestamps if ahora - ts <= ventana]
    return len(recientes) / ventana

def monitor_carga():
    while True:
        current_L = calcular_L()
        T = calcular_T()
        workers_necesarios = max(1, int((current_L * T) / LOAD_PER_WORKER))
        num_workers = len(worker_processes)

        print(f"[Monitor] Mensajes/segundo: {current_L}, Tiempo promedio por mensaje: {T}, Workers actuales: {num_workers}, Necesarios: {workers_necesarios}")

        # Escalar hacia arriba
        if workers_necesarios > num_workers:
            for i in range(workers_necesarios - num_workers):
                puerto = 8001 + len(worker_processes)
                print(f"[Monitor] Lanzando worker en puerto {puerto}")
                proc = subprocess.Popen(["python3", WORKER_SCRIPT, str(puerto)])
                worker_processes.append(f'localhost:{puerto}')

        # Escalar hacia abajo solo si NO hay tareas pendientes
        elif workers_necesarios < num_workers :
            excess = num_workers - workers_necesarios
            for i in range(excess):
                try:
                    # Enviar mensaje de despedida antes de matar (si implementas shutdown remoto)
                    observer_url = worker_processes.pop()
                    proxy = xmlrpc.client.ServerProxy(f'http://{observer_url}/RPC2')
                    proxy.shutdown()
                except Exception as e:
                    print(f"[Monitor] Error notificando al worker: {e}")
                finally:
                    proc.terminate()
                    print(f"[Monitor] Terminando worker con insulto. Quedan {len(worker_processes)} procesos activos.")
        time.sleep(1)

# Crear servidor
with SimpleXMLRPCServer(('localhost', 8000), requestHandler=RequestHandler, allow_none=True) as server:
    server.register_introspection_functions()

    def add_insults(insult):
        timestamp = time.time()
        mensaje_timestamps.append(timestamp)
        if insult in insult_list:
            return "Insult already exists!"
        insult_list.append(insult)
        notify(insult)
        return f"{insult} afegit!"

    server.register_function(add_insults, 'add_insults')

    def get_insults():
        timestamp = time.time()
        mensaje_timestamps.append(timestamp)
        return insult_list

    server.register_function(get_insults, 'get_insults')

    def insult_me():
        timestamp = time.time()
        mensaje_timestamps.append(timestamp)
        return random.choice(insult_list)

    server.register_function(insult_me, 'insult_me')

    def subscribe(observerURL):
        timestamp = time.time()
        mensaje_timestamps.append(timestamp)
        observers.append(observerURL)
        return f"You have been subscribed to the server {ownURL}"

    server.register_function(subscribe, 'subscribe')

    def subscribeServer(serverURL):
        timestamp = time.time()
        mensaje_timestamps.append(timestamp)
        if serverURL not in serverObservers:
            serverObservers.append(serverURL)
            print(f"[Subscripción] Nuevo servidor: {serverURL}")
        return f"Servidor registrado en {ownURL}"

    server.register_function(subscribeServer, 'subscribeServer')

    def notify(new_insult):
        timestamp = time.time()
        mensaje_timestamps.append(timestamp)
        for observer_url in serverObservers:
            try:
                proxy = xmlrpc.client.ServerProxy(f'http://{observer_url}/RPC2')
                proxy.notify(new_insult)
            except Exception as e:
                print(f"[Error] Notificando a {observer_url}: {e}")

    def notifyServers(new_insult):
        timestamp = time.time()
        mensaje_timestamps.append(timestamp)
        for observer_url in observers:
            try:
                proxy = xmlrpc.client.ServerProxy(f'http://{observer_url}/RPC2')
                proxy.notify(new_insult)
                proxy.add_insults(new_insult)
            except Exception as e:
                print(f"[Error] Notificando observer {observer_url}: {e}")

    def periodic_insult():
        while True:
            for observer_url in observers:
                try:
                    proxy = xmlrpc.client.ServerProxy(f'http://{observer_url}/RPC2')
                    insult = insult_me()
                    proxy.recive(insult)
                except Exception as e:
                    print(f"[Error] Enviando insulto periódico a {observer_url}: {e}")
            time.sleep(5)

    def enviar_texto(texto):
        timestamp = time.time()
        mensaje_timestamps.append(timestamp)
        print(f"[Entrada] Texto encolado: {texto}")
        work_queue.put(texto)
        return "Texto recibido y encolado."

    server.register_function(enviar_texto, 'enviar_texto')

    def get_filtered():
        timestamp = time.time()
        mensaje_timestamps.append(timestamp)
        return filtered_results

    server.register_function(get_filtered, 'get_filtered')

    class MyFuncs:
        def mul(self, x, y):
            return x * y

    server.register_instance(MyFuncs())

    # Iniciar hilos secundarios
    threading.Thread(target=periodic_insult, daemon=True).start()
    threading.Thread(target=distribuir_trabajo, daemon=True).start()
    threading.Thread(target=monitor_carga, daemon=True).start()

    print("[Servidor] Servidor principal iniciado en puerto 8000")
    server.serve_forever()
