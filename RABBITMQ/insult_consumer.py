import pika
import redis
import time

WAIT_TIMEOUT = 1  # segundos entre intentos
MAX_IDLE_CHECKS = 5  # número máximo de intentos sin recibir mensajes

def main():
    # Conectar a Redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    # Conectar a RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='insults')
    channel.basic_qos(prefetch_count=1)

    print('Waiting for insults...')

    idle_checks = 0

    while idle_checks < MAX_IDLE_CHECKS:
        method_frame, properties, body = channel.basic_get(queue='insults', auto_ack=True)
        if method_frame:
            idle_checks = 0  # reiniciar contador si hay mensaje
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
