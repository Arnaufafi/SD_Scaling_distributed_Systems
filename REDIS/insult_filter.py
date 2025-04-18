import pika
import redis
import time

QUEUE_NAME = 'text_queue'

def main():
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0)

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    # Fair dispatch (one message at a time per worker)
    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        text = body.decode('utf-8')
        insults = [i.decode('utf-8') for i in r.lrange('INSULTS', 0, -1)]

        clean_text = text
        for insult in insults:
            clean_text = clean_text.replace(insult, "CENSORED")

        # Store cleaned text in RESULTS list
        r.rpush('RESULTS', clean_text)

        print(f"[Filter {id(callback)}] Cleaned: {clean_text}")
        time.sleep(1)  # Simulate processing delay

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(f"[Filter {id(callback)}] Waiting for messages...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Filter stopped.")
        connection.close()

if __name__ == '__main__':
    main()
