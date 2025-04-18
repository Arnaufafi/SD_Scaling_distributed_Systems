import pika
import redis

def main():
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0)

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='insults')

    def callback(ch, method, properties, body):
        insult = body.decode('utf-8')
        r.sadd('insults', insult)

    channel.basic_consume(queue='insults', on_message_callback=callback, auto_ack=True)

    print('Waiting for insults. To exit press CTRL+C')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Consumer stopped.")
    finally:
        connection.close()

if __name__ == '__main__':
    main()
