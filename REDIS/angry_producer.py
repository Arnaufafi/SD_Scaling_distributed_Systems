import pika
import time
import random

QUEUE_NAME = 'text_queue'
ANGRY_TEXTS = [
    "You're such a fool!",
    "This is stupid.",
    "You absolute idiot.",
    "You’re the worst programmer ever.",
    "That was a dumb move."
]

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    try:
        text = random.choice(ANGRY_TEXTS)
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=text.encode())
        print(f"[AngryProducer] Sent: {text}")
        time.sleep(3)
    except KeyboardInterrupt:
        print("AngryProducer stopped.")
        connection.close()

if __name__ == '__main__':
    main()
