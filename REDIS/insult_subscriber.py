import pika
import sys

EXCHANGE_NAME = 'insult_broadcast'

def main():
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the same fanout exchange
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='fanout')

    # Create a new, unique queue with a random name (exclusive, auto-deleted)
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind it to the fanout exchange
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name)

    print(f"[Receiver] Waiting for insults... (Queue: {queue_name})")

    def callback(ch, method, properties, body):
        print(f"[Receiver] Got insult: {body.decode()}")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Receiver stopped.")
        connection.close()
        sys.exit(0)

if __name__ == '__main__':
    main()
