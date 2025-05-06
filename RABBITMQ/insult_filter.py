import pika
import redis
import time

QUEUE_NAME = 'text_queue'
RESULT_QUEUE = 'RESULTS'
INSULT_REFRESH_INTERVAL = 10  # segundos

def connect_redis():
    return redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def refresh_insults(r):
    return set(r.smembers('insults'))

def process_message(body, insults):
    words = body.split()
    return ' '.join('CENSORED' if word in insults else word for word in words)

def main():
    r = connect_redis()
    insults = refresh_insults(r)
    last_refresh = time.time()

    def callback(ch, method, properties, body):
        nonlocal insults, last_refresh

        body_str = body.decode('utf-8')

        # Refresh insults list periodically
        now = time.time()
        if now - last_refresh > INSULT_REFRESH_INTERVAL:
            insults = refresh_insults(r)
            last_refresh = now

        cleaned = process_message(body_str, insults)

        # Store result
        r.rpush(RESULT_QUEUE, cleaned)
        print(f"[Filter] Cleaned: {cleaned}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    # RabbitMQ setup
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print("[Filter] Waiting for messages...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == '__main__':
    main()
