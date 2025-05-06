import redis

# Connect to Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

queue_name = "insults"
list_name = "insults_list"
print("Consumer is waiting for tasks...")

while True:
    task = client.blpop(queue_name, timeout=1)  # Wait up to 1 second
    if task:
        insult = task[1]
        client.sadd(list_name, insult)
        print(f"Consumed and added: {insult}")
    else:
        print("No tasks received in the last second. Shutting down.")
        break
