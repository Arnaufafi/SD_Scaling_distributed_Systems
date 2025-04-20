import sys
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import queue
import threading

# Leer el puerto desde los argumentos
if len(sys.argv) != 2:
    print("Uso: python3 xmlrpcServer.py <puerto>")
    sys.exit(1)

port = int(sys.argv[1])
ownURL = f"localhost:{port}"

# Restrict to a particular path
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Lista local de insultos
insult_list = ["Nyicris", "Cap de suro", "Estaquirot", "AIXAFAGUITARRES", "BRÈTOL", "CURT DE GAMBALS", "TANOCA", "TÒTIL", "GAMARÚS", "TAP DE BASSA", "CAGABANDÚRRIES", "Mosqueta morta", "Mort de gana", "POCA-SOLTA", "BANDARRA"]

# Observers locales (por si queremos añadir lógica futura)
observers = []

# Cola y resultados locales (solo se usan internamente)
work_queue = queue.Queue()
filtered_results = []


def censurar_insultos(text):
    print(f"[Worker:{port}] Censurando texto...")
    censored = text
    for insult in insult_list:
        censored = censored.replace(insult, "CENSURADO")
    return censored

def add_insults(insult):
    if insult not in insult_list:
        insult_list.append(insult)
        print(f"[Worker:{port}] Nuevo insulto añadido: {insult}")
        return f"{insult} añadido"
    return "Insulto ya existente"

def notify(new_insult):
    return add_insults(new_insult)

# Método para apagar el servidor
def shutdown():
    print(f"[Worker:{port}] Shutdown recibido. Cerrando servidor suavemente...")
    threading.Thread(target=server.shutdown).start()  # Llamada al shutdown en un hilo separado
    return f"Worker {port} cerrándose..."

# Crear servidor
with SimpleXMLRPCServer(('localhost', port), requestHandler=RequestHandler, allow_none=True) as server:
    server.register_introspection_functions()

    # Registrar funciones expuestas
    server.register_function(censurar_insultos, 'censurar_insultos')
    server.register_function(add_insults, 'add_insults')
    server.register_function(notify, 'notify')
    server.register_function(shutdown, 'shutdown')

    print(f"[Worker] Servidor iniciado en puerto {port}")
    server.serve_forever()

    print(f"[Worker] Servidor en puerto {port} terminado. Bye!")
