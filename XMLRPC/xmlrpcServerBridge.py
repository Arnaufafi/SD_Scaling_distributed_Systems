from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import random
import xmlrpc.client
import threading
import time
import queue
import subprocess

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
                resultado = proxy.censurar_insultos(texto)
                filtered_results.append(resultado)
                print(f"[Trabajo] Texto censurado por {observer_url}: {resultado}")
            except Exception as e:
                print(f"[Error] Enviando a {observer_url}: {e}")
        else:
            print("[Aviso] No hay servidores disponibles para procesar texto.")
        work_queue.task_done()
        time.sleep(0.2)

def monitor_carga():
    while True:
        tareas_pendientes = work_queue.qsize()
        num_workers = len(worker_processes)
        workers_necesarios = tareas_pendientes // LOAD_PER_WORKER 
        
        if workers_necesarios < 1:
            workers_necesarios = 1

        print(f"[Monitor] Tareas: {tareas_pendientes}, Workers actuales: {num_workers}, Necesarios: {workers_necesarios}")

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
        if insult in insult_list:
            return "Insult already exists!"
        insult_list.append(insult)
        notify(insult)
        return f"{insult} afegit!"

    server.register_function(add_insults, 'add_insults')

    def get_insults():
        return insult_list

    server.register_function(get_insults, 'get_insults')

    def insult_me():
        return random.choice(insult_list)

    server.register_function(insult_me, 'insult_me')

    def subscribe(observerURL):
        observers.append(observerURL)
        return f"You have been subscribed to the server {ownURL}"

    server.register_function(subscribe, 'subscribe')

    def subscribeServer(serverURL):
        if serverURL not in serverObservers:
            serverObservers.append(serverURL)
            print(f"[Subscripción] Nuevo servidor: {serverURL}")
        return f"Servidor registrado en {ownURL}"

    server.register_function(subscribeServer, 'subscribeServer')

    def notify(new_insult):
        for observer_url in serverObservers:
            try:
                proxy = xmlrpc.client.ServerProxy(f'http://{observer_url}/RPC2')
                proxy.notify(new_insult)
            except Exception as e:
                print(f"[Error] Notificando a {observer_url}: {e}")

    def notifyServers(new_insult):
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
        print(f"[Entrada] Texto encolado: {texto}")
        work_queue.put(texto)
        return "Texto recibido y encolado."

    server.register_function(enviar_texto, 'enviar_texto')

    def get_filtered():
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
