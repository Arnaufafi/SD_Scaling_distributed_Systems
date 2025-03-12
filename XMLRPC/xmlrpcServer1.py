from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import random
import xmlrpc.client
import time

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Lista de insultos
insult_list = ["Nyicris", "Cap de suro", "Estaquirot", "AIXAFAGUITARRES", "BRÈTOL", "CURT DE GAMBALS", "TANOCA", "TÒTIL", "GAMARÚS", "TAP DE BASSA", "CAGABANDÚRRIES", "Mosqueta morta", "Mort de gana", "POCA-SOLTA", "BANDARRA"]
observers = []
ownURL = 'localhost/8000'

# Crear servidor
with SimpleXMLRPCServer(('localhost', 8000), requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    # Método para añadir insultos
    def add_insults(insult):
        insult_list.append(insult)
        notify(insult)  # Notificar a los observadores cuando se añada un insulto
        print(insult + "afegit!")
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
        for observer_url in observers:
            try:
                print(f"Notifying {observer_url} about the new insult: {new_insult}")
                proxy = xmlrpc.client.ServerProxy(f'http://{observer_url}/RPC2')
                proxy.add_insults(new_insult)
            except Exception as e:
                print(f"Error notifying {observer_url}: {e}")

    # Instancia para otros métodos (por ejemplo, multiplicación)
    class MyFuncs:
        def mul(self, x, y):
            return x * y

    server.register_instance(MyFuncs())

    # Ejecutar el servidor
    server.serve_forever()