import pika
import time
import random

QUEUE_NAME = 'text_queue'
CLEAN_TEXTS = [
    "Have a wonderful day!",
    "You are doing great!",
    "Keep up the good work!",
    "It's sunny outside!",
    "Coding is fun and rewarding."
]

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    try:
        text = random.choice(CLEAN_TEXTS)
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=text.encode())
        print(f"[TextProducer] Sent: {text}")
        time.sleep(5)
    except KeyboardInterrupt:
        print("TextProducer stopped.")
        connection.close()

if __name__ == '__main__':
    main()
