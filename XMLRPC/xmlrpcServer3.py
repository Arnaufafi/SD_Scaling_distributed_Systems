from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import random
import xmlrpc.client
import threading
import time
import queue

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Lista de insultos
insult_list = ["Nyicris", "Cap de suro", "Estaquirot", "AIXAFAGUITARRES", "BRÈTOL", "CURT DE GAMBALS", "TANOCA", "TÒTIL", "GAMARÚS", "TAP DE BASSA", "CAGABANDÚRRIES", "Mosqueta morta", "Mort de gana", "POCA-SOLTA", "BANDARRA"]
observers = []
serverObservers = []
ownURL = 'localhost/8002'

# Cola de trabajo y resultados filtrados
work_queue = queue.Queue()
filtered_results = []

# Función para censurar insultos
def censurar_insultos(text):
    censored = text
    for insult in insult_list:
        censored = censored.replace(insult, "CENSURADO")
    return censored

# Trabajador de la cola
def trabajador():
    while True:
        text = work_queue.get()
        filtered = censurar_insultos(text)
        filtered_results.append(filtered)
        print(f"Texto procesado: {filtered}")
        work_queue.task_done()

# Lanzar trabajador
threading.Thread(target=trabajador, daemon=True).start()

# Crear servidor
with SimpleXMLRPCServer(('localhost', 8002), requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    # Método para añadir insultos
    def add_insults(insult):
        # Comprobar si el insulto ya existe
        if insult in insult_list:
            print("Insult already exists!")
            return "Insult already exists!"
        else :
            insult_list.append(insult)
            notify(insult)  # Notificar a los observadores cuando se añada un insulto
            print(insult + " afegit!")
            return f"{insult} afegit!"

    server.register_function(add_insults, 'add_insults')

    # Método para obtener insultos
    def get_insults():
        return insult_list

    server.register_function(get_insults, 'get_insults')

    # Método para insultar aleatoriamente
    def insult_me():
        randnum = random.randint(0, len(insult_list) - 1)  # Ajuste del índice para evitar IndexError
        return insult_list[randnum]

    server.register_function(insult_me, 'insult_me')

    # Método para suscribirse a un observador
    def subscribe(observerURL):
        print(f"Observer: Attached an observer: {observerURL}")
        observers.append(observerURL)
        return f"You have been subscribed to the server {ownURL}"

    server.register_function(subscribe, 'subscribe')

    # Método de notificación
    def notify(new_insult):
        # Enviar a todos los observadores la nueva lista de insultos
        for observer_url in serverObservers:
            try:
                print(f"Notifying {observer_url} about the new insult: {new_insult}")
                proxy = xmlrpc.client.ServerProxy(f'http://{observer_url}/RPC2')
                proxy.notify(new_insult)
            except Exception as e:
                print(f"Error notifying {observer_url}: {e}")

    # Método de notificación
    def notifyServers(new_insult):
        # Enviar a todos los observadores la nueva lista de insultos
        for observer_url in observers:
            try:
                print(f"Notifying {observer_url} about the new insult: {new_insult}")
                proxy = xmlrpc.client.ServerProxy(f'http://{observer_url}/RPC2')
                proxy.notify(new_insult)
                proxy.add_insults(new_insult)
            except Exception as e:
                print(f"Error notifying {observer_url}: {e}")

    # Método de eventos periodicos
    def periodic_insult():
        # Enviar a todos los observadores la nueva lista de insultos
        while True:
            for observer_url in observers:
                try:
                    print(f"Enviant insult als observers")
                    proxy = xmlrpc.client.ServerProxy(f'http://{observer_url}/RPC2')
                    insult = insult_me()
                    proxy.recive(insult)
                except Exception as e:
                    print(f"Error notifying {observer_url}: {e}")
            time.sleep(5)

    def enviar_texto(texto):
        print(f"Texto recibido para censura: {texto}")
        work_queue.put(texto)
        return "Texto recibido y encolado."

    server.register_function(enviar_texto, 'enviar_texto')

    # Obtener textos ya procesados
    def get_filtered():
        return filtered_results

    server.register_function(get_filtered, 'get_filtered')

    # Instancia para otros métodos (por ejemplo, multiplicación)
    class MyFuncs:
        def mul(self, x, y):
            return x * y

    server.register_instance(MyFuncs())

    thread = threading.Thread(target=periodic_insult, daemon=True)
    thread.start()

    # Ejecutar el servidor
    server.serve_forever()