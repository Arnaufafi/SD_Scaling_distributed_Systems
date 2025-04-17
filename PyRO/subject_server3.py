import Pyro4
import threading
import queue
import time
import random

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Observable:
    def __init__(self):
        self.observers = []  # List to store observer references
        self.serverObservers = []       # Pyro Observers
        self.observersServers = []      # Pyro Servers
        self.insult_list = ["Nyicris", "Cap de suro", "Estaquirot", "AIXAFAGUITARRES", "BRÈTOL", "CURT DE GAMBALS", "TANOCA", "TÒTIL", "GAMARÚS", "TAP DE BASSA", "CAGABANDÚRRIES", "Mosqueta morta", "Mort de gana", "POCA-SOLTA", "BANDARRA"]
        self.work_queue = queue.Queue()
        self.filtered_results = []

        threading.Thread(target=self.trabajador, daemon=True).start()
        threading.Thread(target=self.periodic_insult, daemon=True).start()

    def register_observer(self, observer_uri):
        """Register an observer using its remote URI."""
        observer = Pyro4.Proxy(observer_uri)  # Convert URI into a Pyro proxy
        self.observers.append(observer)
        print(f"Observer {observer_uri} registered.")

    def unregister_observer(self, observer_uri):
        """Unregister an observer."""
        self.observers = [obs for obs in self.observers if obs._pyroUri != observer_uri]
        print(f"Observer {observer_uri} unregistered.")

    def notify_observers(self, message):
        """Notify all registered observers."""
        print("Notifying observers...")
        for observer in self.observers:
            try:
                observer.update(message)  # Remote method call
            except Pyro4.errors.CommunicationError:
                print(f"Observer {observer._pyroUri} unreachable. Removing.")
                self.observers.remove(observer)
    
    def add_insults(self, insult):
            if insult not in self.insult_list:
                self.insult_list.append(insult)
                print(f"Nuevo insulto añadido: {insult}")
                self.notify(insult)
                self.notifyServers(insult)

    def get_insults(self):
        return self.insult_list

    def insult_me(self):
        return random.choice(self.insult_list)    

    def notify(self, new_insult):
        for observer in self.observers:
            try:
                print(f"Notificando a {observer._pyroUri} del nuevo insulto: {new_insult}")
                observer.notify(new_insult)
            except Exception as e:
                print(f"Error notificando a {observer._pyroUri}: {e}")
                self.observers.remove(observer)

    def notifyServer(self, new_insult):
        for observer in self.observersServers:
            try:
                print(f"Notificando a {observer._pyroUri} del nuevo insulto: {new_insult}")
                observer.notify(new_insult)
                observer.add_insults(new_insult)
            except Exception as e:
                print(f"Error notificando a {observer._pyroUri}: {e}")
                self.observers.remove(observer)
    
    def periodic_insult(self):
        while True:
            insult = self.insult_me()
            for observer in self.observers:
                try:
                    print(f"Enviando insulto periódico a {observer._pyroUri}: {insult}")
                    observer.recive(insult)
                except Exception as e:
                    print(f"Error enviando insulto periódico: {e}")
                    self.observers.remove(observer)
            time.sleep(5)
    
    def censurar_insultos(self, text):
        censored = text
        for insult in self.insult_list:
            censored = censored.replace(insult, "CENSURADO")
        return censored

    def trabajador(self):
        while True:
            text = self.work_queue.get()
            filtered = self.censurar_insultos(text)
            self.filtered_results.append(filtered)
            print(f"Texto procesado: {filtered}")
            self.work_queue.task_done()

    def enviar_texto(self, texto):
        print(f"Texto recibido: {texto}")
        self.work_queue.put(texto)
        return "Texto recibido y encolado."

    def get_filtered(self):
        return self.filtered_results
    


# Start the Pyro daemon and register the observable object
def start_server():
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(Observable)
    ns.register("server3.observable", uri)
    print(f"Observable server is running. URI: {uri}")
    daemon.requestLoop()

if __name__ == "__main__":
    start_server()
