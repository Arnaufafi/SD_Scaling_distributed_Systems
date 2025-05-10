from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import random
import xmlrpc.client
import threading
import time
import queue

# Restrict to a particular path
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# List of insults
insult_list = ["Nyicris", "Cap de suro", "Estaquirot", "AIXAFAGUITARRES", "BRÈTOL", "CURT DE GAMBALS", "TANOCA", "TÒTIL", "GAMARÚS", "TAP DE BASSA", "CAGABANDÚRRIES", "Mosqueta morta", "Mort de gana", "POCA-SOLTA", "BANDARRA"]
observers = []
serverObservers = []
ownURL = 'localhost/8001'

# Work queue and filtered results
work_queue = queue.Queue()
filtered_results = []

# Function to censor insults
def censor_insults(text):
    censored = text
    for insult in insult_list:
        censored = censored.replace(insult, "CENSORED")
    return censored

# Queue worker
def worker():
    while True:
        text = work_queue.get()
        filtered = censor_insults(text)
        filtered_results.append(filtered)
        print(f"Processed text: {filtered}")
        work_queue.task_done()

# Launch worker
threading.Thread(target=worker, daemon=True).start()

# Create server
with SimpleXMLRPCServer(('localhost', 8001), requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    # Method to add insults
    def add_insults(insult):
        if insult in insult_list:
            print("Insult already exists!")
            return "Insult already exists!"
        else:
            insult_list.append(insult)
            print(insult + " added!")
            return f"{insult} added!"

    server.register_function(add_insults, 'add_insults')

    # Method to get insults
    def get_insults():
        return insult_list

    server.register_function(get_insults, 'get_insults')

    # Method to get a random insult
    def insult_me():
        randnum = random.randint(0, len(insult_list) - 1)
        return insult_list[randnum]

    server.register_function(insult_me, 'insult_me')

    # Method to subscribe an observer
    def subscribe(observerURL):
        print(f"Observer: Attached an observer: {observerURL}")
        observers.append(observerURL)
        return f"You have been subscribed to the server {ownURL}"

    server.register_function(subscribe, 'subscribe')

    # Method to subscribe a server
    def subscribeServer(serverURL):
        print(f"Observer: Attached a server: {serverURL}")
        serverObservers.append(serverURL)
        return f"You have been subscribed to the server {ownURL}"

    server.register_function(subscribeServer, 'subscribeServer')

    # Periodic event method
    def periodic_insult():
        while True:
            for observer_url in observers:
                try:
                    print(f"Sending insult to observers")
                    proxy = xmlrpc.client.ServerProxy(f'http://{observer_url}/RPC2')
                    insult = insult_me()
                    proxy.recive(insult)
                except Exception as e:
                    print(f"Error notifying {observer_url}: {e}")
            time.sleep(5)

    def send_text(text):
        print(f"Text received for censorship: {text}")
        work_queue.put(text)
        return "Text received and enqueued."

    server.register_function(send_text, 'enviar_texto')

    # Get already processed texts
    def get_filtered():
        return filtered_results

    server.register_function(get_filtered, 'get_filtered')

    # Instance for other methods (e.g., multiplication)
    class MyFuncs:
        def mul(self, x, y):
            return x * y

    server.register_instance(MyFuncs())

    thread = threading.Thread(target=periodic_insult, daemon=True)
    thread.start()

    # Run the server
    server.serve_forever()
