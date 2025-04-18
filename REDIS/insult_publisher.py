import pika
import redis
import time
import random

EXCHANGE_NAME = 'insult_broadcast'

def main():
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0)

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare a fanout exchange
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='fanout')

    # Get all insults from Redis
    insults = r.smembers('insults')

    while True:
        insult = random.sample(list(insults), 1)[0]
        message = insult.decode('utf-8')
        channel.basic_publish(exchange=EXCHANGE_NAME, routing_key='', body=message)
        print(f"[Broadcaster] Sent: {message}")
        time.sleep(5)  # Optional: Delay between messages
        insults = r.smembers('insults')
    connection.close()

if __name__ == '__main__':
    main()
