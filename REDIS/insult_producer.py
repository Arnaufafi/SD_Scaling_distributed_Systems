import redis
import time

# Connect to Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

queue_name = "insults_queue"

# Send multiple messages
tasks = ["Bobo", "Vinicius", "Pozo", "Pozinho", "Pozão", "Pozudo", "Pozãozudo"]

for task in tasks:
    client.rpush(queue_name, task)
    print(f"Produced: {task}")