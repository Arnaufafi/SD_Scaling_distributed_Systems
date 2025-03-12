import redis
import time

# Connect to Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

channel_name = "insult_broadcast"
list_name = "insults_list"
messages = client.smembers(list_name)

for message in messages:
    client.publish(channel_name, message)
    print(f"Published: {message}")
    time.sleep(2)  # Simulating delay between messages