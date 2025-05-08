import subprocess
import time
import pika
from concurrent.futures import ThreadPoolExecutor

# Configuración de RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
queue_name = 'text_queue'
result_queue = 'RESULTS'
channel.queue_delete(queue=queue_name)
channel.queue_delete(queue=result_queue)
connection.close()

NUM_EXECUTIONS = 200
client_scripts = (
    ["RABBITMQ/text_producer.py"] * NUM_EXECUTIONS +
    ["RABBITMQ/angry_producer.py"] * NUM_EXECUTIONS +
    ["RABBITMQ/insult_producer.py"] * 50
)

def run_script(script):
    p = subprocess.Popen(["python3", script])
    p.wait()

def fill_queue():
    print("[client] Filling the queue with tasks...")
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=1000) as executor:
        executor.map(run_script, client_scripts)
    end_time = time.time()
    print(f"[client] Queue filled in {end_time - start_time:.2f} seconds.")

if __name__ == '__main__':
    fill_queue()
