import subprocess
import time
import pika
import random
from concurrent.futures import ThreadPoolExecutor

# Configuración de RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
queue_name = 'text_queue'
result_queue = 'RESULTS'
channel.queue_delete(queue=queue_name)
channel.queue_delete(queue=result_queue)
connection.close()

def run_script(script):
    p = subprocess.Popen(["python3", script])
    p.wait()

def fill_queue():
    for i in range(2):  # Ejecutar 3 veces
        num_executions = random.randint(100, 300)
        client_scripts = (
            ["text_producer.py"] * num_executions +
            ["angry_producer.py"] * num_executions
        )

        print(f"[client] Iteración {i+1}: Llenando la cola con {num_executions} tareas...")
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=1000) as executor:
            executor.map(run_script, client_scripts)
        end_time = time.time()
        print(f"[client] Cola llena en {end_time - start_time:.2f} segundos.")

        time.sleep(1)  # Pausa de 1 segundo

if __name__ == '__main__':
    fill_queue()
