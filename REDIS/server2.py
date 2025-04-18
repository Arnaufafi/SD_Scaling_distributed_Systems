import multiprocessing
import insult_producer, insult_publisher, insult_filter

def run_insult_producer():
    insult_producer.main()

def run_insult_broadcaster():
    insult_publisher.main()

def run_insult_filter():
    insult_filter.main()

if __name__ == '__main__':
    print("[SERVER] Starting all services...")
    processes = [
        multiprocessing.Process(target=run_insult_producer),
        multiprocessing.Process(target=run_insult_broadcaster),
        multiprocessing.Process(target=run_insult_filter)
    ]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
