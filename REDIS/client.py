import multiprocessing
import insult_consumer, insult_subscriber, text_producer, angry_producer
import time  # Importar módulo para medir tiempo

# Número de instancias a lanzar por tipo

NUM_RECEIVERS = 100
NUM_TEXT_PRODUCERS = 5
NUM_ANGRY_PRODUCERS = 5


def run_insult_receiver():
    insult_subscriber.main()

def run_text_producer():
    text_producer.main()

def run_angry_producer():
    angry_producer.main()

if __name__ == '__main__':
    print("[CLIENT] Starting all components...")

    # Registrar el tiempo de inicio
    start_time = time.time()

    processes = []
    
    # Suscriptores (insult_receiver.py)
    for _ in range(NUM_RECEIVERS):
        processes.append(multiprocessing.Process(target=run_insult_receiver))

    # Productores de texto sin insultos
    for _ in range(NUM_TEXT_PRODUCERS):
        processes.append(multiprocessing.Process(target=run_text_producer))

    # Productores de texto con insultos
    for _ in range(NUM_ANGRY_PRODUCERS):
        processes.append(multiprocessing.Process(target=run_angry_producer))

    # Iniciar todos los procesos
    for p in processes:
        p.start()

    # Esperar a que todos los procesos terminen
    for p in processes:
        p.join()

    # Registrar el tiempo de finalización
    end_time = time.time()

    # Calcular la duración
    elapsed_time = end_time - start_time
    print(f"[CLIENT] All components finished in {elapsed_time:.2f} seconds.")
