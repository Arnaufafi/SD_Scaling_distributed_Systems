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
        self.insult_list = [
            "Nyicris", "Blockhead", "Beanpole", "GUITAR-CRUSHER", "BRAT", "SLOW-WITTED",
            "DUMBHEAD", "DIMWIT", "FOOL", "MUDPLUGGER", "TWADDLE-TALKER", 
            "Fainthearted", "Starveling", "GOOD-FOR-NOTHING", "SCALLYWAG"
        ]
        self.work_queue = queue.Queue()
        self.filtered_results = []

        threading.Thread(target=self.worker, daemon=True).start()
        threading.Thread(target=self.periodic_insult, daemon=True).start()

    def register_observer(self, observer_uri):
        """Register an observer using its remote URI."""
        observer = Pyro4.Proxy(observer_uri)
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
                observer.update(message)
            except Pyro4.errors.CommunicationError:
                print(f"Observer {observer._pyroUri} unreachable. Removing.")
                self.observers.remove(observer)
    
    def add_insults(self, insult):
        if insult not in self.insult_list:
            self.insult_list.append(insult)
            print(f"New insult added: {insult}")
            self.notify(insult)
            self.notify_server(insult)

    def get_insults(self):
        return self.insult_list

    def insult_me(self):
        return random.choice(self.insult_list)    

    def notify(self, new_insult):
        for observer in self.observers:
            try:
                print(f"Notifying {observer._pyroUri} about new insult: {new_insult}")
                observer.notify(new_insult)
            except Exception as e:
                print(f"Error notifying {observer._pyroUri}: {e}")
                self.observers.remove(observer)

    def notify_server(self, new_insult):
        for observer in self.observersServers:
            try:
                print(f"Notifying server {observer._pyroUri} about new insult: {new_insult}")
                observer.notify(new_insult)
                observer.add_insults(new_insult)
            except Exception as e:
                print(f"Error notifying server {observer._pyroUri}: {e}")
                self.observers.remove(observer)
    
    def periodic_insult(self):
        while True:
            insult = self.insult_me()
            for observer in self.observers:
                try:
                    print(f"Sending periodic insult to {observer._pyroUri}: {insult}")
                    observer.recive(insult)
                except Exception as e:
                    print(f"Error sending periodic insult: {e}")
                    self.observers.remove(observer)
            time.sleep(5)
    
    def censor_insults(self, text):
        censored = text
        for insult in self.insult_list:
            censored = censored.replace(insult, "CENSORED")
        return censored

    def worker(self):
        while True:
            text = self.work_queue.get()
            filtered = self.censor_insults(text)
            self.filtered_results.append(filtered)
            print(f"Processed text: {filtered}")
            self.work_queue.task_done()

    def send_text(self, text):
        print(f"Received text: {text}")
        self.work_queue.put(text)
        return "Text received and queued."

    def get_filtered(self):
        return self.filtered_results
    

# Start the Pyro daemon and register the observable object
def start_server():
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(Observable)
    ns.register("server1.observable", uri)
    print(f"Observable server is running. URI: {uri}")
    daemon.requestLoop()

if __name__ == "__main__":
    start_server()
