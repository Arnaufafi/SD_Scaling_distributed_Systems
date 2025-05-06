import redis
import time

# Connect to Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

queue_name = "work_queue"

# Send multiple messages
tasks = ["Redis", "Bloquejant", "Consumidor", "Productor", "Cua", "Tasca", "Consumida", "Produïda"]

for task in tasks:
    client.rpush(queue_name, task)
    print(f"Produced: {task}")