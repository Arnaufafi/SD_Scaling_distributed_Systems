import pika
import redis
import time

WAIT_TIMEOUT = 1  # seconds between attempts
MAX_IDLE_CHECKS = 5  # maximum number of attempts without receiving messages

def main():
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='insults')
    channel.basic_qos(prefetch_count=1)

    print('Waiting for insults...')

    idle_checks = 0

    while idle_checks < MAX_IDLE_CHECKS:
        method_frame, properties, body = channel.basic_get(queue='insults', auto_ack=True)
        if method_frame:
            idle_checks = 0  # reset counter if message received
            insult = body.decode('utf-8')
            r.sadd('insults', insult)
            print(f"Received and stored insult: {insult}")
        else:
            idle_checks += 1

    print("No more insults. Exiting.")
    channel.close()
    connection.close()

if __name__ == '__main__':
    main()
