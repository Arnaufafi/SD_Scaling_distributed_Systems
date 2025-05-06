import pika
import random

INSULTS = [
    "idiot",
    "stupid",
    "dumb",
    "fool",
]

def send_insult(channel):
    insult = random.choice(INSULTS)
    channel.basic_publish(exchange='', routing_key='insults', body=insult)
    print(f"Sent insult: {insult}")

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='insults')

    try:
        for _ in range(10):
            send_insult(channel)
            #time.sleep(5)
    except KeyboardInterrupt:
        print("Producer stopped.")
    finally:
        connection.close()

if __name__ == '__main__':
    main()
