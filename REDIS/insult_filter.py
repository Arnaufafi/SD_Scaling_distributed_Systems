import redis

# Connect to Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

queue_name = "work_queue"
result_name = "result_list"
censor_list = "insults_list"
print("Consumer is waiting for tasks...")

while True:
    task = client.blpop(queue_name, timeout=1)  # Espera máximo 1 segundo por una tarea
    if task:
        result = list(map(
            lambda word: '****' if word in client.smembers(censor_list) else word,
            task[1].split()
        ))
        result = ' '.join(result)
        client.sadd(result_name, result)
        print(f"Consumed and added: {result}")
    else:
        print("No tasks received in the last second. Exiting.")
        break
