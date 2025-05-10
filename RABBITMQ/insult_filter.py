import pika
import redis

# Configuration
QUEUE_NAME = 'text_queue'
RESULT_NAME = 'RESULTS'
CENSOR_LIST = 'insults'
WAIT_TIMEOUT = 1  # seconds
MAX_IDLE_CHECKS = 5  # To exit if the queue remains empty

# Connect to Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME, durable=False)
channel.basic_qos(prefetch_count=1)

print("Consumer is waiting for tasks...")

idle_checks = 0

def process_and_store(message):
    insults = client.smembers(CENSOR_LIST)  # Get all insults only once
    words = message.split()
    censored = [
        '****' if word in insults else word
        for word in words
    ]
    result = ' '.join(censored)
    client.sadd(RESULT_NAME, result)
    print(f"Consumed and added: {result}")

while idle_checks < MAX_IDLE_CHECKS:
    method_frame, properties, body = channel.basic_get(queue=QUEUE_NAME, auto_ack=False)

    if method_frame:
        idle_checks = 0  # reset if something is received
        message = body.decode('utf-8')
        process_and_store(message)
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    else:
        idle_checks += 1

# Clean shutdown
print("No more tasks. Exiting.")

channel.close()
connection.close()
